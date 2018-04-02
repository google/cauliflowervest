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

"""Tests for commandline module."""

import StringIO



from absl.testing import absltest
import mock

from cauliflowervest.client import base_client
from cauliflowervest.client.mac import commandline


class CommandLineTest(absltest.TestCase):
  """Test the `CommandLine` abstract base class."""

  def setUp(self):
    server_url = 'www.fakeserver.com'
    username = 'fakeuser'
    self.cmd = commandline.CommandLine(server_url, username)

  def testMissingActionFlag(self):
    action = ''
    volume = None
    ret = self.cmd.Execute(action, volume)
    self.assertEqual(commandline.RET_MISSING_ACTION_FLAG, ret)

  def testUnknownAction(self):
    action = 'nonexistent action'
    volume = None
    ret = self.cmd.Execute(action, volume)
    self.assertEqual(commandline.RET_UNKNOWN_ACTION_FLAG, ret)

  def testDisplayPassphraseMissingVolumeFlag(self):
    action = commandline.ACTION_DISPLAY
    volume = None
    ret = self.cmd.Execute(action, volume)
    self.assertEqual(commandline.RET_MISSING_VOLUME_FLAG, ret)

  def testRevertVolumeMissingVolumeFlag(self):
    action = commandline.ACTION_REVERT
    volume = None
    ret = self.cmd.Execute(action, volume)
    self.assertEqual(commandline.RET_MISSING_VOLUME_FLAG, ret)

  def testUnlockVolumeMissingVolumeFlag(self):
    action = commandline.ACTION_UNLOCK
    volume = None
    ret = self.cmd.Execute(action, volume)
    self.assertEqual(commandline.RET_MISSING_VOLUME_FLAG, ret)

  @mock.patch.object(commandline.CommandLine, 'Client')
  @mock.patch('sys.stdout', new_callable=StringIO.StringIO)
  def testDisplayPassphrase(self, mock_stdout, mock_client):
    action = commandline.ACTION_DISPLAY
    volume = 'fakevolume'
    mock_client.return_value.RetrieveSecret.return_value = 'passphrase'
    ret = self.cmd.Execute(action, volume)
    self.assertEqual(commandline.RET_SUCCESS, ret)
    self.assertEqual(mock_stdout.getvalue(), 'passphrase\n')

  @mock.patch('getpass.getpass')
  @mock.patch.object(commandline.CommandLine, 'Client')
  @mock.patch.object(commandline.glue, 'GetStorage')
  def testRevertVolume(self, mock_storage, mock_client, mock_getpass):
    action = commandline.ACTION_REVERT
    volume = 'fakevolume'
    passphrase = 'fakepassphrase'
    mock_getpass.return_value = 'password'
    mock_storage.return_value.RevertVolume.return_value = True
    mock_client.return_value.RetrieveSecret.return_value = passphrase
    ret = self.cmd.Execute(action, volume)
    self.assertEqual(commandline.RET_SUCCESS, ret)
    mock_storage.return_value.RevertVolume.assert_has_calls(
        [mock.call(volume, passphrase, mock.ANY)])

  @mock.patch.object(commandline.CommandLine, 'Client')
  @mock.patch.object(commandline.glue, 'GetStorage')
  def testUnlockVolume(self, mock_storage, mock_client):
    action = commandline.ACTION_UNLOCK
    volume = 'fakevolume'
    passphrase = 'fakepassphrase'
    mock_client.return_value.RetrieveSecret.return_value = passphrase
    mock_storage.return_value.UnlockVolume.return_value = True
    ret = self.cmd.Execute(action, volume)
    self.assertEqual(commandline.RET_SUCCESS, ret)
    mock_storage.return_value.UnlockVolume.assert_has_calls(
        [mock.call(volume, passphrase)])

  @mock.patch('getpass.getpass')
  @mock.patch.object(commandline.CommandLine, 'Client')
  @mock.patch.object(commandline.glue, 'GetStorage')
  @mock.patch.object(commandline.glue, 'UpdateEscrowPassphrase')
  @mock.patch.object(commandline.glue, 'SaveVolumeUUID')
  def testRotateRecoveryKey(self, mock_save, mock_update, mock_storage,
                            mock_client, mock_getpass):
    action = commandline.ACTION_ROTATE
    volume = 'fakevolume'
    passphrase = 'fakepassphrase'
    recovery_key = 'fakerecoverykey'
    mock_getpass.return_value = 'password'
    mock_client.return_value.RetrieveSecret.return_value = passphrase
    mock_client.return_value.UploadPassphrase.return_value = True
    mock_storage.return_value.GetPrimaryVolumeUUID.return_value = volume
    mock_update.return_value = recovery_key
    mock_save.return_value = True
    mocks = mock.Mock()
    mocks.attach_mock(mock_storage.return_value.GetPrimaryVolumeUUID,
                      'GetPrimaryVolumeUUID')
    mocks.attach_mock(mock_client.return_value.RetrieveSecret, 'RetrieveSecret')
    mocks.attach_mock(mock_client.return_value.UploadPassphrase,
                      'UploadPassphrase')
    mocks.attach_mock(mock_update, 'UpdateEscrowPassphrase')
    mocks.attach_mock(mock_save, 'SaveVolumeUUID')

    ret = self.cmd.Execute(action, volume)

    self.assertEqual(commandline.RET_SUCCESS, ret)
    mocks.assert_has_calls([
        mock.call.GetPrimaryVolumeUUID(),
        mock.call.RetrieveSecret(volume),
        mock.call.UpdateEscrowPassphrase(mock.ANY, passphrase),
        mock.call.UploadPassphrase(volume, recovery_key),
        mock.call.SaveVolumeUUID(volume, mock.ANY),
    ])


class CommandlineOAuth2Test(absltest.TestCase):
  """Test the `CommandLineOAuth2` class."""

  def setUp(self):
    server_url = 'www.fakeserver.com'
    username = 'fakeuser'
    self.cmd = commandline.CommandLineOAuth2(server_url, username)

  @mock.patch('getpass.getpass')
  @mock.patch.object(commandline, 'base_client')
  def testBadOAuth2Credentials(self, mock_bc, mock_getpass):
    action = commandline.ACTION_DISPLAY
    volume = 'fakevolume'
    mock_getpass.return_value = 'password'
    # Must unmock the AuthenticationError class:
    mock_bc.AuthenticationError = base_client.AuthenticationError
    mock_bc.GetOauthCredentials.side_effect = base_client.AuthenticationError(
        'Authentication has failed')
    ret = self.cmd.Execute(action, volume)
    self.assertEqual(commandline.RET_OAUTH2_FAILED, ret)

  @mock.patch('getpass.getpass')
  @mock.patch.object(commandline, 'base_client')
  @mock.patch.object(commandline.client, 'FileVaultClient')
  def testBadMetadata(self, mock_fvc, mock_bc, mock_getpass):
    action = 'display'
    volume = 'fakevolume'
    mock_getpass.return_value = 'password'
    # Must unmock the MetadataError class:
    mock_bc.MetadataError = base_client.MetadataError
    (mock_fvc.return_value.GetAndValidateMetadata
     .side_effect) = base_client.MetadataError('Required metadata is not found')
    ret = self.cmd.Execute(action, volume)
    self.assertEqual(commandline.RET_MACHINE_METADATA_ERROR, ret)




if __name__ == '__main__':
  absltest.main()
