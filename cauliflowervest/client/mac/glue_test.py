# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for main module."""

import logging
import os
import plistlib



import mock

from absl.testing import absltest

from cauliflowervest.client import util
from cauliflowervest.client.mac import client
from cauliflowervest.client.mac import glue


class FdesetupApplyEncryptionTest(absltest.TestCase):
  """ApplyEncryptionTest which uses fdesetup as the encryption tool."""

  # Test data has long lines: pylint: disable=g-line-too-long
  OUTPUT = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>EnabledDate</key>
  <string>2012-10-09 14:01:55 -0400</string>
  <key>HardwareUUID</key>
  <string>F934ABE5-O5K9-1035-B04D-AO4203LLO034</string>
  <key>LVGUUID</key>
  <string>19A65A81-9AD9-473D-AD65-7E933B338D23</string>
  <key>LVUUID</key>
  <string>217CEC95-018C-4CA5-964F-4E7235CA2937</string>
  <key>PVUUID</key>
  <string>8D5D3D81-0F1B-4311-9804-1E5FA087D1B4</string>
  <key>RecoveryKey</key>
  <string>DLEV-ZYT9-ODLA-PVML-66DV-HZ8R</string>
  <key>SerialNumber</key>
  <string>W53035EINFA</string>
</dict>
</plist>
""".strip()

  def setUp(self):
    super(FdesetupApplyEncryptionTest, self).setUp()

    self.mock_user = 'luser'
    self.mock_pass = 'password123'
    self.mock_fvclient = mock.Mock(spec=client.FileVaultClient)

    def _ExistSideEffect(path):
      if path == glue.FullDiskEncryptionSetup.PATH:
        return True
      assert False
    self.patches = [
        mock.patch.object(util, 'RetrieveEntropy', return_value='entropy'),
        mock.patch.object(util, 'SupplyEntropy'),
        mock.patch.object(util, 'GetPlistFromExec'),
        mock.patch.object(os.path, 'exists', side_effect=_ExistSideEffect),
    ]
    for m in self.patches:
      m.start()

  def tearDown(self):
    for m in self.patches:
      m.stop()
    super(FdesetupApplyEncryptionTest, self).tearDown()

  def _CommonAsserts(self):
    self.assertIn(
        glue.FullDiskEncryptionSetup.PATH,
        util.GetPlistFromExec.call_args_list[0][0][0])
    self.assertIn(
        self.mock_pass, util.GetPlistFromExec.call_args_list[0][1]['stdin'])
    util.SupplyEntropy.assert_called_once_with('entropy')

  @mock.patch.object(glue, 'GetFilesystemType', return_value='hfs')
  def testAuthFail(self, _):
    mock_exc = glue.util.ExecError(
        returncode=glue.FullDiskEncryptionSetup.RETURN_AUTH_FAIL)
    util.GetPlistFromExec.side_effect = mock_exc

    self.assertRaises(
        glue.InputError,
        glue.ApplyEncryption,
        self.mock_fvclient, self.mock_user, self.mock_pass)

    self._CommonAsserts()

  @mock.patch.object(glue, 'GetFilesystemType', return_value='hfs')
  @mock.patch.object(logging, 'error')
  def testGenericFail(self, error_mock, _):
    mock_exc = glue.util.ExecError(returncode=1)
    util.GetPlistFromExec.side_effect = mock_exc

    self.assertRaises(
        glue.Error,
        glue.ApplyEncryption,
        self.mock_fvclient, self.mock_user, self.mock_pass)

    self._CommonAsserts()
    error_mock.assert_called_once()

  @mock.patch.object(glue, 'GetFilesystemType', return_value='hfs')
  def testOk(self, _):
    pl = plistlib.readPlistFromString(self.OUTPUT)
    util.GetPlistFromExec.return_value = pl

    self.mock_fvclient.SetOwner(self.mock_user)

    result = glue.ApplyEncryption(
        self.mock_fvclient, self.mock_user, self.mock_pass)
    self.assertEqual(
        ('217CEC95-018C-4CA5-964F-4E7235CA2937',
         'DLEV-ZYT9-ODLA-PVML-66DV-HZ8R'),
        result)

    self._CommonAsserts()


class CheckEncryptionPreconditionsTest(absltest.TestCase):
  """Test the CheckEncryptionPreconditions() function."""

  @mock.patch.object(glue, 'GetFilesystemType', return_value='hfs')
  @mock.patch.object(os.path, 'exists', return_value=False)
  @mock.patch.object(
      glue.corestorage.CoreStorage, 'GetRecoveryPartition',
      return_value='/dev/disk0s3')
  def testOk(self, get_recovery_partition_mock, exists_mock, _):
    glue.CheckEncryptionPreconditions()

    get_recovery_partition_mock.assert_called_once()
    exists_mock.assert_called_once_with(
        '/Library/Keychains/FileVaultMaster.keychain')

  @mock.patch.object(glue, 'GetFilesystemType', return_value='hfs')
  @mock.patch.object(os.path, 'exists', return_value=True)
  @mock.patch.object(
      glue.corestorage.CoreStorage, 'GetRecoveryPartition',
      return_value='/dev/disk0s3')
  def testKeychainPresent(self, get_recovery_partition_mock, exists_mock, _):
    self.assertRaises(glue.OptionError, glue.CheckEncryptionPreconditions)

    get_recovery_partition_mock.assert_called_once()

    get_recovery_partition_mock.assert_called_once()
    exists_mock.assert_called_once_with(
        '/Library/Keychains/FileVaultMaster.keychain')

  @mock.patch.object(glue, 'GetFilesystemType', return_value='hfs')
  @mock.patch.object(
      glue.corestorage.CoreStorage, 'GetRecoveryPartition', return_value=None)
  def testMissingRecovery(self, unused_cs_mock, unused_fstype_mock):
    """Test CheckEncryptionPreconditions()."""
    self.assertRaises(glue.OptionError, glue.CheckEncryptionPreconditions)


if __name__ == '__main__':
  absltest.main()
