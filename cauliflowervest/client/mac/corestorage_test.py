#
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
#
#
"""Tests for corestorage module."""

import plistlib
import uuid



import mock

from absl.testing import absltest

from cauliflowervest.client import util
from cauliflowervest.client.mac import corestorage


DISKUTIL = '/usr/sbin/diskutil'

# Line too long; pylint: disable=g-line-too-long
CORE_STORAGE_PLIST_LIST_EMPTY = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict/>
</plist>
""".strip()
CORE_STORAGE_PLIST_LIST_ENABLED = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CoreStorageLogicalVolumeGroups</key>
  <array>
    <dict>
      <key>CoreStorageLogicalVolumeFamilies</key>
      <array>
        <dict>
          <key>CoreStorageLogicalVolumes</key>
          <array>
            <dict>
              <key>CoreStorageRole</key>
              <string>LV</string>
              <key>CoreStorageUUID</key>
              <string>F93A24E9-C8DB-4E83-8EB0-FDEC3C029B9D</string>
            </dict>
          </array>
          <key>CoreStorageRole</key>
          <string>LVF</string>
          <key>CoreStorageUUID</key>
          <string>F550F600-D0C3-40C2-AE18-BBEB5197283F</string>
        </dict>
      </array>
      <key>CoreStoragePhysicalVolumes</key>
      <array>
        <dict>
          <key>CoreStorageRole</key>
          <string>PV</string>
          <key>CoreStorageUUID</key>
          <string>70646750-969C-44D9-AEE7-F761F667ECC0</string>
        </dict>
      </array>
      <key>CoreStorageRole</key>
      <string>LVG</string>
      <key>CoreStorageUUID</key>
      <string>977A78C8-786F-418B-B14E-D3BB01576AD5</string>
    </dict>
  </array>
</dict>
</plist>
""".strip()

CORE_STORAGE_PLIST_LVF_INFO_ENCRYPTED = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CoreStorageLogicalVolumeFamilyEncryptionStatus</key>
  <string>Unlocked</string>
  <key>CoreStorageLogicalVolumeFamilyEncryptionType</key>
  <string>AES-XTS</string>
  <key>CoreStorageRole</key>
  <string>LVF</string>
  <key>CoreStorageRoleUserVisibleName</key>
  <string>Logical Volume Family</string>
  <key>CoreStorageUUID</key>
  <string>E7E7F5BB-EF8B-40A7-AD8F-A6CABC1E3B4F</string>
  <key>MemberOfCoreStorageLogicalVolumeGroup</key>
  <string>90B4D2FE-AD6B-4B68-A917-990B34D2F2E0</string>
</dict>
</plist>
""".strip()
CORE_STORAGE_PLIST_LVF_INFO_ENABLED = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CoreStorageLogicalVolumeFamilyEncryptionStatus</key>
  <string>Unlocked</string>
  <key>CoreStorageLogicalVolumeFamilyEncryptionType</key>
  <string>None</string>
  <key>CoreStorageRole</key>
  <string>LVF</string>
  <key>CoreStorageRoleUserVisibleName</key>
  <string>Logical Volume Family</string>
  <key>CoreStorageUUID</key>
  <string>E7E7F5BB-EF8B-40A7-AD8F-A6CABC1E3B4F</string>
  <key>MemberOfCoreStorageLogicalVolumeGroup</key>
  <string>90B4D2FE-AD6B-4B68-A917-990B34D2F2E0</string>
</dict>
</plist>
""".strip()
CORE_STORAGE_PLIST_LV_INFO = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CoreStorageLogicalVolumeBytesConverted</key>
  <integer>59831853056</integer>
  <key>CoreStorageLogicalVolumeContentHint</key>
  <string>Apple_HFS</string>
  <key>CoreStorageLogicalVolumeConversionState</key>
  <string>Complete</string>
  <key>CoreStorageLogicalVolumeName</key>
  <string>Untitled 1</string>
  <key>CoreStorageLogicalVolumeSequence</key>
  <integer>4</integer>
  <key>CoreStorageLogicalVolumeSize</key>
  <integer>59831853056</integer>
  <key>CoreStorageLogicalVolumeStatus</key>
  <string>Online</string>
  <key>CoreStorageLogicalVolumeVersion</key>
  <integer>65536</integer>
  <key>CoreStorageRole</key>
  <string>LV</string>
  <key>CoreStorageRoleUserVisibleName</key>
  <string>Logical Volume</string>
  <key>CoreStorageUUID</key>
  <string>32996E98-BC03-4DFB-A195-FC17581D016E</string>
  <key>DeviceIdentifier</key>
  <string>disk1</string>
  <key>MemberOfCoreStorageLogicalVolumeFamily</key>
  <string>96895DD6-6BBD-4847-88F3-1B0AA0FED043</string>
  <key>MemberOfCoreStorageLogicalVolumeGroup</key>
  <string>77EEE38D-6E6C-49E0-BD78-4FB0EA226B8C</string>
  <key>VolumeName</key>
  <string>Untitled 1</string>
</dict>
</plist>
""".strip()
DISKUTIL_LIST_PLIST = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>AllDisks</key>
  <array>
    <string>disk0</string>
    <string>disk0s1</string>
    <string>disk0s2</string>
    <string>disk0s3</string>
  </array>
  <key>AllDisksAndPartitions</key>
  <array>
    <dict>
      <key>Content</key>
      <string>GUID_partition_scheme</string>
      <key>DeviceIdentifier</key>
      <string>disk0</string>
      <key>Partitions</key>
      <array>
        <dict>
          <key>Content</key>
          <string>EFI</string>
          <key>DeviceIdentifier</key>
          <string>disk0s1</string>
          <key>Size</key>
          <integer>209715200</integer>
        </dict>
        <dict>
          <key>Content</key>
          <string>Apple_HFS</string>
          <key>DeviceIdentifier</key>
          <string>disk0s2</string>
          <key>MountPoint</key>
          <string>/</string>
          <key>Size</key>
          <integer>120473067520</integer>
          <key>VolumeName</key>
          <string>MacintoshHD</string>
        </dict>
        <dict>
          <key>Content</key>
          <string>Apple_Boot</string>
          <key>DeviceIdentifier</key>
          <string>disk0s3</string>
          <key>Size</key>
          <integer>650002432</integer>
          <key>VolumeName</key>
          <string>Recovery HD</string>
        </dict>
      </array>
      <key>Size</key>
      <integer>121332826112</integer>
    </dict>
  </array>
  <key>VolumesFromDisks</key>
  <array>
    <string>MacintoshHD</string>
  </array>
  <key>WholeDisks</key>
  <array>
    <string>disk0</string>
  </array>
</dict>
</plist>
"""


class CoreStorageTest(absltest.TestCase):
  """Test the core storage related features."""

  @mock.patch.object(util, 'GetPlistFromExec', side_effect=util.ExecError)
  def testIsBootVolumeEncryptedWhenNotCoreStorage(self, _):
    cs = corestorage.CoreStorage()
    self.assertEqual(False, cs.IsBootVolumeEncrypted())

  @mock.patch.object(util, 'GetPlistFromExec')
  def testIsBootVolumeEncryptedWhenNoLVFInfo(self, get_plist_from_exec_mock):
    lvf_uuid = 'bad uuid'

    get_plist_from_exec_mock.side_effect = [
        {'MemberOfCoreStorageLogicalVolumeFamily': lvf_uuid},
        util.ExecError]
    cs = corestorage.CoreStorage()
    self.assertEqual(False, cs.IsBootVolumeEncrypted())

    get_plist_from_exec_mock.assert_has_calls([
        mock.call(('/usr/sbin/diskutil', 'cs', 'info', '-plist', '/')),
        mock.call(('/usr/sbin/diskutil', 'cs', 'info', '-plist', lvf_uuid))])

  @mock.patch.object(util, 'GetPlistFromExec')
  def testIsBootVolumeEncryptedWhenEncrypted(self, get_plist_from_exec_mock):
    lvf_uuid = 'bad uuid'

    get_plist_from_exec_mock.side_effect = [
        {'MemberOfCoreStorageLogicalVolumeFamily': lvf_uuid},
        {'CoreStorageLogicalVolumeFamilyEncryptionType': 'AES-XTS'},
    ]

    cs = corestorage.CoreStorage()
    self.assertEqual(True, cs.IsBootVolumeEncrypted())

    get_plist_from_exec_mock.assert_has_calls([
        mock.call(('/usr/sbin/diskutil', 'cs', 'info', '-plist', '/')),
        mock.call(('/usr/sbin/diskutil', 'cs', 'info', '-plist', lvf_uuid))])

  @mock.patch.object(util, 'GetPlistFromExec')
  def testIsBootVolumeEncryptedWhenCoreStorageButNotEncrypted(
      self, get_plist_from_exec_mock):
    lvf_uuid = 'bad uuid'

    get_plist_from_exec_mock.side_effect = [
        {'MemberOfCoreStorageLogicalVolumeFamily': lvf_uuid},
        {'CoreStorageLogicalVolumeFamilyEncryptionType': '---something---'},
    ]

    cs = corestorage.CoreStorage()
    self.assertEqual(False, cs.IsBootVolumeEncrypted())

    get_plist_from_exec_mock.assert_has_calls([
        mock.call(('/usr/sbin/diskutil', 'cs', 'info', '-plist', '/')),
        mock.call(('/usr/sbin/diskutil', 'cs', 'info', '-plist', lvf_uuid))])

  @mock.patch.object(util, 'GetPlistFromExec')
  def testGetRecoveryPartition(self, get_plist_from_exec_mock):
    pl = plistlib.readPlistFromString(DISKUTIL_LIST_PLIST)
    get_plist_from_exec_mock.return_value = pl

    cs = corestorage.CoreStorage()
    self.assertEqual(cs.GetRecoveryPartition(), '/dev/disk0s3')

    get_plist_from_exec_mock.assert_called_once()

  @mock.patch.object(util, 'GetPlistFromExec', side_effect=util.ExecError)
  def testGetRecoveryPartitionWhenDiskutilFail(self, _):
    cs = corestorage.CoreStorage()
    self.assertEqual(cs.GetRecoveryPartition(), None)

  @mock.patch.object(util, 'GetPlistFromExec')
  def testGetCoreStorageStateNone(self, get_plist_from_exec_mock):
    pl = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LIST_EMPTY)
    get_plist_from_exec_mock.return_value = pl

    cs = corestorage.CoreStorage()
    self.assertEqual(cs.GetState(), corestorage.State.NONE)

    get_plist_from_exec_mock.assert_called_once_with(
        ['/usr/sbin/diskutil', 'corestorage', 'list', '-plist'])

  @mock.patch.object(util, 'GetPlistFromExec')
  def testGetCoreStorageStateEncrypted(self, get_plist_from_exec_mock):
    pl = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LIST_ENABLED)
    pl2 = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LVF_INFO_ENCRYPTED)
    pl3 = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LV_INFO)

    get_plist_from_exec_mock.side_effect = [pl, pl2, pl3]

    cs = corestorage.CoreStorage()
    self.assertEqual(cs.GetState(), corestorage.State.ENCRYPTED)
    get_plist_from_exec_mock.assert_has_calls([
        mock.call(['/usr/sbin/diskutil', 'corestorage', 'list', '-plist']),
        mock.call([
            '/usr/sbin/diskutil', 'corestorage', 'info', '-plist',
            'F550F600-D0C3-40C2-AE18-BBEB5197283F']),
        mock.call([
            '/usr/sbin/diskutil', 'corestorage', 'info', '-plist',
            'F93A24E9-C8DB-4E83-8EB0-FDEC3C029B9D'])])

  @mock.patch.object(util, 'GetPlistFromExec')
  def testGetCoreStorageStateEnabled(self, get_plist_from_exec_mock):
    pl = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LIST_ENABLED)
    pl2 = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LVF_INFO_ENABLED)
    pl3 = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LV_INFO)

    get_plist_from_exec_mock.side_effect = [pl, pl2, pl3]

    cs = corestorage.CoreStorage()
    self.assertEqual(cs.GetState(), corestorage.State.ENABLED)

  @mock.patch.object(util, 'GetPlistFromExec')
  def testGetCoreStorageStateFailed(self, get_plist_from_exec_mock):
    pl = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LIST_ENABLED)
    pl2 = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LVF_INFO_ENABLED)
    pl3 = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LV_INFO)
    pl3['CoreStorageLogicalVolumeConversionState'] = 'Failed'

    get_plist_from_exec_mock.side_effect = [pl, pl2, pl3]
    cs = corestorage.CoreStorage()
    self.assertEqual(cs.GetState(), corestorage.State.FAILED)

  @mock.patch.object(util, 'GetPlistFromExec')
  def testGetVolumeSize(self, get_plist_from_exec_mock):
    mock_uuid = str(uuid.uuid4())
    pl = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LV_INFO)
    get_plist_from_exec_mock.return_value = pl

    cs = corestorage.CoreStorage()
    self.assertEqual('55.00 GiB', cs.GetVolumeSize(mock_uuid))

  @mock.patch.object(corestorage.util, 'Exec')
  def testUnlockVolumeAlreadyUnlockedMavericks(self, exec_mock):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())

    exec_mock.return_value = (
        1, '', 'Error beginning CoreStorage Logical Volume unlock: '
        'The target Core Storage volume is not locked (-69748)')

    cs = corestorage.CoreStorage()
    cs.UnlockVolume(mock_uuid, mock_passphrase)

  @mock.patch.object(corestorage.util, 'Exec')
  def testUnlockVolumeAlreadyUnlockedYosemite(self, exec_mock):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())
    exec_mock.return_value = (
        1, '', '%s is already unlocked and is attached as disk1' % mock_uuid)

    cs = corestorage.CoreStorage()
    cs.UnlockVolume(mock_uuid, mock_passphrase)

    exec_mock.assert_called_once_with(
        (DISKUTIL, 'corestorage', 'unlockVolume',
         mock_uuid, '-stdinpassphrase'),
        stdin=mock_passphrase)

  @mock.patch.object(corestorage.util, 'Exec', return_value=(1, '', ''))
  def testUnlockVolumeCantUnlock(self, exec_mock):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())

    cs = corestorage.CoreStorage()
    self.assertRaises(corestorage.CouldNotUnlockError,
                      cs.UnlockVolume, mock_uuid, mock_passphrase)

    exec_mock.assert_called_once_with(
        (DISKUTIL, 'corestorage', 'unlockVolume',
         mock_uuid, '-stdinpassphrase'),
        stdin=mock_passphrase)

  @mock.patch.object(corestorage.util, 'Exec', return_value=(0, '', ''))
  def testUnlockVolumeOk(self, exec_mock):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())

    cs = corestorage.CoreStorage()
    cs.UnlockVolume(mock_uuid, mock_passphrase)

    exec_mock.assert_called_once_with(
        (DISKUTIL, 'corestorage', 'unlockVolume',
         mock_uuid, '-stdinpassphrase'),
        stdin=mock_passphrase)

  @mock.patch.object(corestorage.util, 'Exec', return_value=(1, '', ''))
  @mock.patch.object(corestorage.CoreStorage, 'UnlockVolume')
  def testRevertVolumeCantRevert(self, unlock_volume_mock, exec_mock):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())

    cs = corestorage.CoreStorage()
    self.assertRaises(corestorage.CouldNotRevertError,
                      cs.RevertVolume, mock_uuid, mock_passphrase)

    exec_mock.assert_called_once_with(
        (DISKUTIL, 'corestorage', 'revert', mock_uuid, '-stdinpassphrase'),
        stdin=mock_passphrase)
    unlock_volume_mock.assert_called_once_with(mock_uuid, mock_passphrase)

  @mock.patch.object(corestorage.util, 'Exec', return_value=(0, '', ''))
  @mock.patch.object(corestorage.CoreStorage, 'UnlockVolume')
  def testRevertVolumeOk(self, unlock_volume_mock, exec_mock):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())

    cs = corestorage.CoreStorage()
    cs.RevertVolume(mock_uuid, mock_passphrase)

    unlock_volume_mock.assert_called_once_with(mock_uuid, mock_passphrase)

    exec_mock.assert_called_once_with(
        (DISKUTIL, 'corestorage', 'revert', mock_uuid, '-stdinpassphrase'),
        stdin=mock_passphrase)


if __name__ == '__main__':
  absltest.main()
