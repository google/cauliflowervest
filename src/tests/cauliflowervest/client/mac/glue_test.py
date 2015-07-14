#!/usr/bin/env python
#
# Copyright 2011 Google Inc. All Rights Reserved.
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
## coding=utf-8
#

"""Tests for main module."""



import logging
import plistlib
import unittest

import mox
import stubout

from cauliflowervest.client.mac import client
from cauliflowervest.client.mac import glue


class _ApplyEncryption(object):
  """Base class for ApplyEncryption() tests."""

  def _Prep(self):
    self.mox.StubOutWithMock(glue, 'os')
    self.mox.StubOutWithMock(glue.os, 'path')
    self.mox.StubOutWithMock(glue.util, 'GetPlistFromExec')
    self.mox.StubOutWithMock(glue.util, 'GetRootDisk')
    self.mox.StubOutWithMock(glue.util, 'RetrieveEntropy')
    self.mox.StubOutWithMock(glue.util, 'SupplyEntropy')

    self.mock_user = 'luser'
    self.mock_pass = 'password123'
    self.mock_fvclient = self.mox.CreateMock(client.FileVaultClient)

    glue.util.RetrieveEntropy().AndReturn('entropy')
    glue.util.SupplyEntropy('entropy').AndReturn(None)

  def testAuthFail(self):
    mock_exc = glue.util.ExecError(returncode=self.RETURN_AUTH_FAIL)
    glue.util.GetPlistFromExec(
        mox.In(self.PATH), stdin=mox.StrContains(self.mock_pass)).AndRaise(
            mock_exc)

    self.mox.ReplayAll()
    self.assertRaises(
        glue.InputError,
        glue.ApplyEncryption,
        self.mock_fvclient, self.mock_user, self.mock_pass)
    self.mox.VerifyAll()

  def testGenericFail(self):
    self.mox.StubOutWithMock(logging, 'error')

    mock_exc = glue.util.ExecError(returncode=1)
    glue.util.GetPlistFromExec(
        mox.In(self.PATH), stdin=mox.StrContains(self.mock_pass)).AndRaise(
            mock_exc)
    logging.error(mox.IsA(basestring), mox.IsA(basestring), mox.IgnoreArg())

    self.mox.ReplayAll()
    self.assertRaises(
        glue.Error,
        glue.ApplyEncryption,
        self.mock_fvclient, self.mock_user, self.mock_pass)
    self.mox.VerifyAll()

  def testOk(self):
    pl = plistlib.readPlistFromString(self.OUTPUT)
    glue.util.GetPlistFromExec(
        mox.IsA(tuple), stdin=mox.StrContains(self.mock_pass)).AndReturn(pl)

    self.mock_fvclient.SetOwner(self.mock_user)

    self.mox.ReplayAll()
    result = glue.ApplyEncryption(
        self.mock_fvclient, self.mock_user, self.mock_pass)
    self.assertEquals(
        ('217CEC95-018C-4CA5-964F-4E7235CA2937',
         'DLEV-ZYT9-ODLA-PVML-66DV-HZ8R'),
        result)
    self.mox.VerifyAll()


class CsfdeApplyEncryptionTest(_ApplyEncryption, mox.MoxTestBase):
  """ApplyEncryptionTest which uses csfde as the encryption tool."""

  PATH = glue.CoreStorageFullDiskEncryption.PATH
  RETURN_AUTH_FAIL = glue.CoreStorageFullDiskEncryption.RETURN_AUTH_FAIL
  # Test data has long lines: pylint: disable=g-line-too-long
  OUTPUT = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>LVGUUID</key>
  <string>19A65A81-9AD9-473D-AD65-7E933B338D23</string>
  <key>LVUUID</key>
  <string>217CEC95-018C-4CA5-964F-4E7235CA2937</string>
  <key>PVUUID</key>
  <string>8D5D3D81-0F1B-4311-9804-1E5FA087D1B4</string>
  <key>error</key>
  <false/>
  <key>recovery_password</key>
  <string>DLEV-ZYT9-ODLA-PVML-66DV-HZ8R</string>
</dict>
</plist>
""".strip()

  def setUp(self):
    super(CsfdeApplyEncryptionTest, self).setUp()
    self._Prep()
    glue.os.path.exists(glue.FullDiskEncryptionSetup.PATH).AndReturn(False)
    glue.util.GetRootDisk().AndReturn('/dev/disk0s2')


class FdesetupApplyEncryptionTest(_ApplyEncryption, mox.MoxTestBase):
  """ApplyEncryptionTest which uses fdesetup as the encryption tool."""

  PATH = glue.FullDiskEncryptionSetup.PATH
  RETURN_AUTH_FAIL = glue.FullDiskEncryptionSetup.RETURN_AUTH_FAIL
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
    self._Prep()
    glue.os.path.exists(glue.FullDiskEncryptionSetup.PATH).AndReturn(True)


class CheckEncryptionPreconditionsTest(mox.MoxTestBase):
  """Test the CheckEncryptionPreconditions() function."""

  def setUp(self):
    super(CheckEncryptionPreconditionsTest, self).setUp()
    self.mox = mox.Mox()

  def testOk(self):
    self.mox.StubOutWithMock(glue.corestorage, 'GetRecoveryPartition')
    glue.corestorage.GetRecoveryPartition().AndReturn('/dev/disk0s3')

    self.mox.StubOutWithMock(glue.os, 'path')
    glue.os.path.exists(mox.StrContains('FileVaultMaster')).AndReturn(False)

    self.mox.ReplayAll()
    glue.CheckEncryptionPreconditions()
    self.mox.VerifyAll()

  def testKeychainPresent(self):
    self.mox.StubOutWithMock(glue.corestorage, 'GetRecoveryPartition')
    glue.corestorage.GetRecoveryPartition().AndReturn('/dev/disk0s3')

    self.mox.StubOutWithMock(glue.os, 'path')
    glue.os.path.exists(mox.StrContains('FileVaultMaster')).AndReturn(True)

    self.mox.ReplayAll()
    self.assertRaises(glue.OptionError, glue.CheckEncryptionPreconditions)
    self.mox.VerifyAll()

  def testMissingRecovery(self):
    """Test CheckEncryptionPreconditions()."""
    self.mox.StubOutWithMock(glue.corestorage, 'GetRecoveryPartition')
    glue.corestorage.GetRecoveryPartition().AndReturn(None)

    self.mox.ReplayAll()
    self.assertRaises(glue.OptionError, glue.CheckEncryptionPreconditions)
    self.mox.VerifyAll()


if __name__ == '__main__':
  unittest.main()
