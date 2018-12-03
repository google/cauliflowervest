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

"""Tests for apfs module."""

import plistlib
import uuid



from absl.testing import absltest
import mock

from cauliflowervest.client import util
from cauliflowervest.client.mac import apfs
from cauliflowervest.client.mac import storage


DISKUTIL = '/usr/sbin/diskutil'
FDESETUP = '/usr/bin/fdesetup'
# Line too long; pylint: disable=g-line-too-long
APFS_PLIST_LIST_EMPTY = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict/>
</plist>
""".strip()
APFS_PLIST_LIST_ENABLED = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <key>Containers</key>
        <array>
                <dict>
                        <key>APFSContainerUUID</key>
                        <string>AA2CC5FB-44E2-4677-86AF-66895B9C9956</string>
                        <key>CapacityCeiling</key>
                        <integer>250135076864</integer>
                        <key>CapacityFree</key>
                        <integer>150363664384</integer>
                        <key>ContainerReference</key>
                        <string>disk1</string>
                        <key>DesignatedPhysicalStore</key>
                        <string>disk0s2</string>
                        <key>Fusion</key>
                        <false/>
                        <key>PhysicalStores</key>
                        <array>
                                <dict>
                                        <key>DeviceIdentifier</key>
                                        <string>disk0s2</string>
                                        <key>DiskUUID</key>
                                        <string>9B69F847-83D6-4CB5-A96E-A61B699B1269</string>
                                        <key>Size</key>
                                        <integer>250135076864</integer>
                                </dict>
                        </array>
                        <key>Volumes</key>
                        <array>
                                <dict>
                                        <key>APFSVolumeUUID</key>
                                        <string>C72D5CF6-E9D1-3FCB-A0B0-E3DE83364FD6</string>
                                        <key>CapacityInUse</key>
                                        <integer>97727180800</integer>
                                        <key>CapacityQuota</key>
                                        <integer>0</integer>
                                        <key>CapacityReserve</key>
                                        <integer>0</integer>
                                        <key>CryptoMigrationOn</key>
                                        <false/>
                                        <key>DeviceIdentifier</key>
                                        <string>disk1s1</string>
                                        <key>Encryption</key>
                                        <false/>
                                        <key>Locked</key>
                                        <false/>
                                        <key>Name</key>
                                        <string>Macintosh HD</string>
                                        <key>Roles</key>
                                        <array/>
                                </dict>
                                <dict>
                                        <key>APFSVolumeUUID</key>
                                        <string>518E791C-9D17-4F77-9E86-232B0F71D08F</string>
                                        <key>CapacityInUse</key>
                                        <integer>28352512</integer>
                                        <key>CapacityQuota</key>
                                        <integer>0</integer>
                                        <key>CapacityReserve</key>
                                        <integer>0</integer>
                                        <key>CryptoMigrationOn</key>
                                        <false/>
                                        <key>DeviceIdentifier</key>
                                        <string>disk1s2</string>
                                        <key>Encryption</key>
                                        <false/>
                                        <key>Locked</key>
                                        <false/>
                                        <key>Name</key>
                                        <string>Preboot</string>
                                        <key>Roles</key>
                                        <array>
                                                <string>Preboot</string>
                                        </array>
                                </dict>
                                <dict>
                                        <key>APFSVolumeUUID</key>
                                        <string>DAEED631-B055-4E61-A0DA-FD4037000E3A</string>
                                        <key>CapacityInUse</key>
                                        <integer>506654720</integer>
                                        <key>CapacityQuota</key>
                                        <integer>0</integer>
                                        <key>CapacityReserve</key>
                                        <integer>0</integer>
                                        <key>CryptoMigrationOn</key>
                                        <false/>
                                        <key>DeviceIdentifier</key>
                                        <string>disk1s3</string>
                                        <key>Encryption</key>
                                        <false/>
                                        <key>Locked</key>
                                        <false/>
                                        <key>Name</key>
                                        <string>Recovery</string>
                                        <key>Roles</key>
                                        <array>
                                                <string>Recovery</string>
                                        </array>
                                </dict>
                                <dict>
                                        <key>APFSVolumeUUID</key>
                                        <string>4D50C8C9-81A3-46F2-B3C4-A68F98C86013</string>
                                        <key>CapacityInUse</key>
                                        <integer>1370951680</integer>
                                        <key>CapacityQuota</key>
                                        <integer>0</integer>
                                        <key>CapacityReserve</key>
                                        <integer>0</integer>
                                        <key>CryptoMigrationOn</key>
                                        <false/>
                                        <key>DeviceIdentifier</key>
                                        <string>disk1s4</string>
                                        <key>Encryption</key>
                                        <false/>
                                        <key>Locked</key>
                                        <false/>
                                        <key>Name</key>
                                        <string>VM</string>
                                        <key>Roles</key>
                                        <array>
                                                <string>VM</string>
                                        </array>
                                </dict>
                        </array>
                </dict>
        </array>
</dict>
</plist>
""".strip()


APFS_PLIST_LIST_ENCRYPTED = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <key>Containers</key>
        <array>
                <dict>
                        <key>APFSContainerUUID</key>
                        <string>AA2CC5FB-44E2-4677-86AF-66895B9C9956</string>
                        <key>CapacityCeiling</key>
                        <integer>250135076864</integer>
                        <key>CapacityFree</key>
                        <integer>150363664384</integer>
                        <key>ContainerReference</key>
                        <string>disk1</string>
                        <key>DesignatedPhysicalStore</key>
                        <string>disk0s2</string>
                        <key>Fusion</key>
                        <false/>
                        <key>PhysicalStores</key>
                        <array>
                                <dict>
                                        <key>DeviceIdentifier</key>
                                        <string>disk0s2</string>
                                        <key>DiskUUID</key>
                                        <string>9B69F847-83D6-4CB5-A96E-A61B699B1269</string>
                                        <key>Size</key>
                                        <integer>250135076864</integer>
                                </dict>
                        </array>
                        <key>Volumes</key>
                        <array>
                                <dict>
                                        <key>APFSVolumeUUID</key>
                                        <string>C72D5CF6-E9D1-3FCB-A0B0-E3DE83364FD6</string>
                                        <key>CapacityInUse</key>
                                        <integer>97727180800</integer>
                                        <key>CapacityQuota</key>
                                        <integer>0</integer>
                                        <key>CapacityReserve</key>
                                        <integer>0</integer>
                                        <key>CryptoMigrationOn</key>
                                        <false/>
                                        <key>DeviceIdentifier</key>
                                        <string>disk1s1</string>
                                        <key>Encryption</key>
                                        <true/>
                                        <key>Locked</key>
                                        <false/>
                                        <key>Name</key>
                                        <string>Macintosh HD</string>
                                        <key>Roles</key>
                                        <array/>
                                </dict>
                                <dict>
                                        <key>APFSVolumeUUID</key>
                                        <string>518E791C-9D17-4F77-9E86-232B0F71D08F</string>
                                        <key>CapacityInUse</key>
                                        <integer>28352512</integer>
                                        <key>CapacityQuota</key>
                                        <integer>0</integer>
                                        <key>CapacityReserve</key>
                                        <integer>0</integer>
                                        <key>CryptoMigrationOn</key>
                                        <false/>
                                        <key>DeviceIdentifier</key>
                                        <string>disk1s2</string>
                                        <key>Encryption</key>
                                        <false/>
                                        <key>Locked</key>
                                        <false/>
                                        <key>Name</key>
                                        <string>Preboot</string>
                                        <key>Roles</key>
                                        <array>
                                                <string>Preboot</string>
                                        </array>
                                </dict>
                                <dict>
                                        <key>APFSVolumeUUID</key>
                                        <string>DAEED631-B055-4E61-A0DA-FD4037000E3A</string>
                                        <key>CapacityInUse</key>
                                        <integer>506654720</integer>
                                        <key>CapacityQuota</key>
                                        <integer>0</integer>
                                        <key>CapacityReserve</key>
                                        <integer>0</integer>
                                        <key>CryptoMigrationOn</key>
                                        <false/>
                                        <key>DeviceIdentifier</key>
                                        <string>disk1s3</string>
                                        <key>Encryption</key>
                                        <false/>
                                        <key>Locked</key>
                                        <false/>
                                        <key>Name</key>
                                        <string>Recovery</string>
                                        <key>Roles</key>
                                        <array>
                                                <string>Recovery</string>
                                        </array>
                                </dict>
                                <dict>
                                        <key>APFSVolumeUUID</key>
                                        <string>4D50C8C9-81A3-46F2-B3C4-A68F98C86013</string>
                                        <key>CapacityInUse</key>
                                        <integer>1370951680</integer>
                                        <key>CapacityQuota</key>
                                        <integer>0</integer>
                                        <key>CapacityReserve</key>
                                        <integer>0</integer>
                                        <key>CryptoMigrationOn</key>
                                        <false/>
                                        <key>DeviceIdentifier</key>
                                        <string>disk1s4</string>
                                        <key>Encryption</key>
                                        <false/>
                                        <key>Locked</key>
                                        <false/>
                                        <key>Name</key>
                                        <string>VM</string>
                                        <key>Roles</key>
                                        <array>
                                                <string>VM</string>
                                        </array>
                                </dict>
                        </array>
                </dict>
        </array>
</dict>
</plist>
""".strip()

DISKUTIL_LIST_PLIST = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <key>AllDisks</key>
        <array>
                <string>disk0</string>
                <string>disk0s1</string>
                <string>disk0s2</string>
                <string>disk0s3</string>
                <string>disk1</string>
                <string>disk1s1</string>
                <string>disk1s2</string>
                <string>disk1s3</string>
                <string>disk1s4</string>
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
                                        <key>DiskUUID</key>
                                        <string>0CC213B8-9500-4786-AC84-3C1CB9E6D364</string>
                                        <key>Size</key>
                                        <integer>209715200</integer>
                                        <key>VolumeName</key>
                                        <string>EFI</string>
                                        <key>VolumeUUID</key>
                                        <string>0E239BC6-F960-3107-89CF-1C97F78BB46B</string>
                                </dict>
                                <dict>
                                        <key>Content</key>
                                        <string>Apple_APFS</string>
                                        <key>DeviceIdentifier</key>
                                        <string>disk0s2</string>
                                        <key>DiskUUID</key>
                                        <string>9B69F847-83D6-4CB5-A96E-A61B699B1269</string>
                                        <key>Size</key>
                                        <integer>250135076864</integer>
                                </dict>
                                <dict>
                                        <key>Content</key>
                                        <string>Apple_KernelCoreDump</string>
                                        <key>DeviceIdentifier</key>
                                        <string>disk0s3</string>
                                        <key>DiskUUID</key>
                                        <string>7BE48974-7B31-4985-8280-97E6CB72F0BD</string>
                                        <key>Size</key>
                                        <integer>655360000</integer>
                                </dict>
                        </array>
                        <key>Size</key>
                        <integer>251000193024</integer>
                </dict>
                <dict>
                        <key>APFSVolumes</key>
                        <array>
                                <dict>
                                        <key>DeviceIdentifier</key>
                                        <string>disk1s1</string>
                                        <key>DiskUUID</key>
                                        <string>C72D5CF6-E9D1-3FCB-A0B0-E3DE83364FD6</string>
                                        <key>MountPoint</key>
                                        <string>/</string>
                                        <key>Size</key>
                                        <integer>250135076864</integer>
                                        <key>VolumeName</key>
                                        <string>Macintosh HD</string>
                                        <key>VolumeUUID</key>
                                        <string>C72D5CF6-E9D1-3FCB-A0B0-E3DE83364FD6</string>
                                </dict>
                                <dict>
                                        <key>DeviceIdentifier</key>
                                        <string>disk1s2</string>
                                        <key>DiskUUID</key>
                                        <string>518E791C-9D17-4F77-9E86-232B0F71D08F</string>
                                        <key>Size</key>
                                        <integer>250135076864</integer>
                                        <key>VolumeName</key>
                                        <string>Preboot</string>
                                        <key>VolumeUUID</key>
                                        <string>518E791C-9D17-4F77-9E86-232B0F71D08F</string>
                                </dict>
                                <dict>
                                        <key>DeviceIdentifier</key>
                                        <string>disk1s3</string>
                                        <key>DiskUUID</key>
                                        <string>DAEED631-B055-4E61-A0DA-FD4037000E3A</string>
                                        <key>Size</key>
                                        <integer>250135076864</integer>
                                        <key>VolumeName</key>
                                        <string>Recovery</string>
                                        <key>VolumeUUID</key>
                                        <string>DAEED631-B055-4E61-A0DA-FD4037000E3A</string>
                                </dict>
                                <dict>
                                        <key>DeviceIdentifier</key>
                                        <string>disk1s4</string>
                                        <key>DiskUUID</key>
                                        <string>4D50C8C9-81A3-46F2-B3C4-A68F98C86013</string>
                                        <key>MountPoint</key>
                                        <string>/private/var/vm</string>
                                        <key>Size</key>
                                        <integer>250135076864</integer>
                                        <key>VolumeName</key>
                                        <string>VM</string>
                                        <key>VolumeUUID</key>
                                        <string>4D50C8C9-81A3-46F2-B3C4-A68F98C86013</string>
                                </dict>
                        </array>
                        <key>Content</key>
                        <string>EF57347C-0000-11AA-AA11-00306543ECAC</string>
                        <key>DeviceIdentifier</key>
                        <string>disk1</string>
                        <key>Partitions</key>
                        <array/>
                        <key>Size</key>
                        <integer>250135076864</integer>
                </dict>
        </array>
        <key>VolumesFromDisks</key>
        <array>
                <string>Macintosh HD</string>
                <string>VM</string>
        </array>
        <key>WholeDisks</key>
        <array>
                <string>disk0</string>
                <string>disk1</string>
        </array>
</dict>
</plist>
""".strip()

DISKUTIL_INFO_PLIST = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
        <key>Bootable</key>
        <true/>
        <key>BooterDeviceIdentifier</key>
        <string>disk1s2</string>
        <key>DeviceIdentifier</key>
        <string>disk1s1</string>
        <key>DeviceNode</key>
        <string>/dev/disk1s1</string>
        <key>DiskUUID</key>
        <string>C72D5CF6-E9D1-3FCB-A0B0-E3DE83364FD6</string>
        <key>FilesystemName</key>
        <string>APFS</string>
        <key>FilesystemType</key>
        <string>apfs</string>
        <key>IORegistryEntryName</key>
        <string>Macintosh HD</string>
        <key>MountPoint</key>
        <string>/</string>
        <key>ParentWholeDisk</key>
        <string>disk1</string>
        <key>RecoveryDeviceIdentifier</key>
        <string>disk1s3</string>
        <key>Size</key>
        <integer>250135076864</integer>
        <key>SolidState</key>
        <true/>
        <key>VolumeName</key>
        <string>Macintosh HD</string>
        <key>VolumeSize</key>
        <integer>250135076864</integer>
        <key>VolumeUUID</key>
        <string>C72D5CF6-E9D1-3FCB-A0B0-E3DE83364FD6</string>
        <key>WholeDisk</key>
        <false/>
</dict>
</plist>
""".strip()


class APFSStorageTest(absltest.TestCase):
  """Test the core storage related features."""

  @mock.patch.object(util, 'GetPlistFromExec', side_effect=util.ExecError)
  def testIsBootVolumeEncryptedWhenNotAPFSStorage(self, _):
    volume = apfs.APFSStorage()
    self.assertEqual(False, volume.IsBootVolumeEncrypted())

  @mock.patch.object(util, 'GetPlistFromExec')
  def testIsBootVolumeEncryptedWhenEncrypted(self, get_plist_from_exec_mock):
    p1 = plistlib.readPlistFromString(DISKUTIL_INFO_PLIST)
    p2 = plistlib.readPlistFromString(APFS_PLIST_LIST_ENCRYPTED)
    get_plist_from_exec_mock.side_effect = [p1, p2]

    volume = apfs.APFSStorage()
    self.assertEqual(True, volume.IsBootVolumeEncrypted())

    get_plist_from_exec_mock.assert_has_calls([
        mock.call(['/usr/sbin/diskutil', 'info', '-plist', '/']),
        mock.call(['/usr/sbin/diskutil', 'apfs', 'list', '-plist'])])

  @mock.patch.object(util, 'GetPlistFromExec')
  def testIsBootVolumeEncryptedWhenAPFSStorageButNotEncrypted(
      self, get_plist_from_exec_mock):
    p1 = plistlib.readPlistFromString(DISKUTIL_INFO_PLIST)
    p2 = plistlib.readPlistFromString(APFS_PLIST_LIST_ENABLED)
    get_plist_from_exec_mock.side_effect = [p1, p2]

    volume = apfs.APFSStorage()
    self.assertEqual(False, volume.IsBootVolumeEncrypted())

    get_plist_from_exec_mock.assert_has_calls([
        mock.call(['/usr/sbin/diskutil', 'info', '-plist', '/']),
        mock.call(['/usr/sbin/diskutil', 'apfs', 'list', '-plist'])])

  @mock.patch.object(util, 'GetPlistFromExec')
  def testGetRecoveryPartition(self, get_plist_from_exec_mock):
    pl = plistlib.readPlistFromString(APFS_PLIST_LIST_ENCRYPTED)
    get_plist_from_exec_mock.return_value = pl

    volume = apfs.APFSStorage()
    self.assertEqual(volume.GetRecoveryPartition(), '/dev/disk1s3')

    get_plist_from_exec_mock.assert_called_once()

  @mock.patch.object(util, 'GetPlistFromExec', side_effect=util.ExecError)
  def testGetRecoveryPartitionWhenDiskutilFail(self, _):
    volume = apfs.APFSStorage()
    self.assertEqual(volume.GetRecoveryPartition(), None)

  @mock.patch.object(util, 'GetPlistFromExec')
  def testGetAPFSStorageStateNone(self, get_plist_from_exec_mock):
    pl = plistlib.readPlistFromString(APFS_PLIST_LIST_EMPTY)
    get_plist_from_exec_mock.return_value = pl

    volume = apfs.APFSStorage()
    self.assertEqual(volume.GetState(), apfs.State.NONE)

    get_plist_from_exec_mock.assert_has_calls([
        mock.call(['/usr/sbin/diskutil', 'apfs', 'list', '-plist'])])

  @mock.patch.object(util, 'GetPlistFromExec')
  def testGetAPFSStorageStateEncrypted(self, get_plist_from_exec_mock):
    pl = plistlib.readPlistFromString(APFS_PLIST_LIST_ENCRYPTED)

    get_plist_from_exec_mock.side_effect = [pl]

    volume = apfs.APFSStorage()

    self.assertEqual(volume.GetState(), apfs.State.ENCRYPTED)
    get_plist_from_exec_mock.assert_has_calls([
        mock.call(['/usr/sbin/diskutil', 'apfs', 'list', '-plist'])])

  @mock.patch.object(util, 'GetPlistFromExec')
  def testGetAPFSStorageStateEnabled(self, get_plist_from_exec_mock):
    pl = plistlib.readPlistFromString(APFS_PLIST_LIST_ENABLED)

    get_plist_from_exec_mock.side_effect = [pl]

    volume = apfs.APFSStorage()
    self.assertEqual(volume.GetState(), apfs.State.ENABLED)

  @mock.patch.object(util, 'GetPlistFromExec')
  def testGetAPFSStorageStateFailed(self, get_plist_from_exec_mock):
    p1 = plistlib.readPlistFromString(APFS_PLIST_LIST_ENABLED)
    # Don't actually know how failures are stored.
    p1['Containers'][0]['Volumes'][0]['APFSVolumeConversionState'] = 'Failed'
    get_plist_from_exec_mock.return_value = p1
    volume = apfs.APFSStorage()
    self.assertEqual(volume.GetState(), apfs.State.FAILED)

  @mock.patch.object(util, 'GetPlistFromExec')
  def testGetVolumeSize(self, get_plist_from_exec_mock):
    pl = plistlib.readPlistFromString(APFS_PLIST_LIST_ENABLED)
    mock_uuid = 'C72D5CF6-E9D1-3FCB-A0B0-E3DE83364FD6'
    get_plist_from_exec_mock.return_value = pl
    volume = apfs.APFSStorage()
    self.assertEqual('231.00 GiB', volume.GetVolumeSize(mock_uuid))

  @mock.patch.object(util, 'GetPlistFromExec')
  def testGetVolumeUUID(self, get_plist_from_exec_mock):
    pl = plistlib.readPlistFromString(APFS_PLIST_LIST_ENCRYPTED)
    mock_uuid = 'C72D5CF6-E9D1-3FCB-A0B0-E3DE83364FD6'
    get_plist_from_exec_mock.return_value = pl
    volume = apfs.APFSStorage()
    self.assertEqual(mock_uuid, volume.GetVolumeUUID('disk'))

  @mock.patch.object(apfs.util, 'Exec', return_value=(1, '', ''))
  def testUnlockVolumeCantUnlock(self, exec_mock):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())

    volume = apfs.APFSStorage()
    self.assertRaises(storage.CouldNotUnlockError,
                      volume.UnlockVolume, mock_uuid, mock_passphrase)

    exec_mock.assert_called_once_with(
        (DISKUTIL, 'apfs', 'unlockVolume',
         mock_uuid, '-stdinpassphrase'),
        stdin=mock_passphrase)

  @mock.patch.object(apfs.util, 'Exec', return_value=(0, '', ''))
  def testUnlockVolumeOk(self, exec_mock):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())

    volume = apfs.APFSStorage()
    volume.UnlockVolume(mock_uuid, mock_passphrase)

    exec_mock.assert_called_once_with(
        (DISKUTIL, 'apfs', 'unlockVolume',
         mock_uuid, '-stdinpassphrase'),
        stdin=mock_passphrase)

  @mock.patch.object(apfs.APFSStorage, 'UnlockVolume', return_value=None)
  @mock.patch.object(apfs.util, 'Exec', return_value=(1, '', ''))
  def testRevertVolumeCantRevert(self, revert_exec_mock, unlock_mock):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())

    volume = apfs.APFSStorage()
    self.assertRaises(storage.CouldNotRevertError,
                      volume.RevertVolume, mock_uuid, mock_passphrase)

    revert_exec_mock.assert_called_once_with(
        ('sudo', '-k', '-S', FDESETUP, 'disable'), stdin='\n')
    unlock_mock.assert_called_once_with(mock_uuid, mock_passphrase)

  @mock.patch.object(apfs.APFSStorage, 'UnlockVolume', return_value=None)
  @mock.patch.object(apfs.util, 'Exec', return_value=(0, '', ''))
  def testRevertVolumeOk(self, revert_exec_mock, unlock_mock):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())

    volume = apfs.APFSStorage()
    self.assertEqual(None, volume.RevertVolume(mock_uuid, mock_passphrase))

    revert_exec_mock.assert_called_once_with(
        ('sudo', '-k', '-S', FDESETUP, 'disable'), stdin='\n')
    unlock_mock.assert_called_once_with(mock_uuid, mock_passphrase)


if __name__ == '__main__':
  absltest.main()
