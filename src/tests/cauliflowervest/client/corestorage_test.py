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
# #

"""Tests for main module."""



import plistlib
import unittest
import uuid
import mox
import stubout

from cauliflowervest.client import corestorage
from cauliflowervest.client import util


DISKUTIL = '/usr/sbin/diskutil'

# Line too long; pylint: disable-msg=C6310
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


class CoreStorageTest(mox.MoxTestBase):
  """Test the core storage related features."""

  def setUp(self):
    super(CoreStorageTest, self).setUp()
    self.mox = mox.Mox()

  def tearDown(self):
    self.mox.UnsetStubs()

  def testIsBootVolumeEncryptedWhenNotCoreStorage(self):
    self.mox.StubOutWithMock(util, 'GetPlistFromExec')
    corestorage.util.GetPlistFromExec(mox.In(DISKUTIL)).AndRaise(
        util.ExecError)
    self.mox.ReplayAll()
    self.assertEquals(False, corestorage.IsBootVolumeEncrypted())
    self.mox.VerifyAll()

  def testIsBootVolumeEncryptedWhenNoLVFInfo(self):
    self.mox.StubOutWithMock(util, 'GetPlistFromExec')
    lvf_uuid = 'bad uuid'
    corestorage.util.GetPlistFromExec(mox.In(DISKUTIL)).AndReturn(
        {'MemberOfCoreStorageLogicalVolumeFamily': lvf_uuid})
    corestorage.util.GetPlistFromExec(
        (DISKUTIL, 'cs', 'info', '-plist', lvf_uuid)).AndRaise(util.ExecError)
    self.mox.ReplayAll()
    self.assertEquals(False, corestorage.IsBootVolumeEncrypted())
    self.mox.VerifyAll()

  def testIsBootVolumeEncryptedWhenEncrypted(self):
    self.mox.StubOutWithMock(util, 'GetPlistFromExec')
    lvf_uuid = 'bad uuid'
    corestorage.util.GetPlistFromExec(mox.In(DISKUTIL)).AndReturn(
        {'MemberOfCoreStorageLogicalVolumeFamily': lvf_uuid})
    corestorage.util.GetPlistFromExec(
        (DISKUTIL, 'cs', 'info', '-plist', lvf_uuid)).AndReturn(
            {'CoreStorageLogicalVolumeFamilyEncryptionType': 'AES-XTS'})
    self.mox.ReplayAll()
    self.assertEquals(True, corestorage.IsBootVolumeEncrypted())
    self.mox.VerifyAll()

  def testIsBootVolumeEncryptedWhenCoreStorageButNotEncrypted(self):
    self.mox.StubOutWithMock(util, 'GetPlistFromExec')
    lvf_uuid = 'bad uuid'
    corestorage.util.GetPlistFromExec(mox.In(DISKUTIL)).AndReturn(
        {'MemberOfCoreStorageLogicalVolumeFamily': lvf_uuid})
    corestorage.util.GetPlistFromExec(
        (corestorage.DISKUTIL, 'cs', 'info', '-plist', lvf_uuid)).AndReturn(
            {'CoreStorageLogicalVolumeFamilyEncryptionType': '---something---'})
    self.mox.ReplayAll()
    self.assertEquals(False, corestorage.IsBootVolumeEncrypted())
    self.mox.VerifyAll()

  def testGetRecoveryPartition(self):
    self.mox.StubOutWithMock(util, 'GetPlistFromExec')
    pl = plistlib.readPlistFromString(DISKUTIL_LIST_PLIST)
    util.GetPlistFromExec(mox.In(DISKUTIL)).AndReturn(pl)
    self.mox.ReplayAll()
    self.assertEquals(corestorage.GetRecoveryPartition(), '/dev/disk0s3')
    self.mox.VerifyAll()

  def testGetRecoveryPartitionWhenDiskutilFail(self):
    self.mox.StubOutWithMock(util, 'GetPlistFromExec')
    util.GetPlistFromExec(mox.In(DISKUTIL)).AndRaise(
        corestorage.util.ExecError)
    self.mox.ReplayAll()
    self.assertEquals(corestorage.GetRecoveryPartition(), None)
    self.mox.VerifyAll()

  def testGetCoreStorageStateNone(self):
    self.mox.StubOutWithMock(util, 'GetPlistFromExec')
    pl = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LIST_EMPTY)
    util.GetPlistFromExec(mox.In(DISKUTIL)).AndReturn(pl)
    self.mox.ReplayAll()
    self.assertEquals(corestorage.GetState(), corestorage.State.none)
    self.mox.VerifyAll()

  def testGetCoreStorageStateEncrypted(self):
    self.mox.StubOutWithMock(util, 'GetPlistFromExec')
    pl = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LIST_ENABLED)
    pl2 = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LVF_INFO_ENCRYPTED)
    util.GetPlistFromExec(mox.In(DISKUTIL)).AndReturn(pl)
    util.GetPlistFromExec(mox.In(DISKUTIL)).AndReturn(pl2)
    self.mox.ReplayAll()
    self.assertEquals(corestorage.GetState(), corestorage.State.encrypted)
    self.mox.VerifyAll()

  def testGetCoreStorageStateEnabled(self):
    self.mox.StubOutWithMock(util, 'GetPlistFromExec')
    pl = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LIST_ENABLED)
    pl2 = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LVF_INFO_ENABLED)
    util.GetPlistFromExec(mox.In(DISKUTIL)).AndReturn(pl)
    util.GetPlistFromExec(mox.In(DISKUTIL)).AndReturn(pl2)
    self.mox.ReplayAll()
    self.assertEquals(corestorage.GetState(), corestorage.State.enabled)
    self.mox.VerifyAll()

  def testGetVolumeSize(self):
    mock_uuid = str(uuid.uuid4())
    self.mox.StubOutWithMock(corestorage.util, 'GetPlistFromExec')
    pl = plistlib.readPlistFromString(CORE_STORAGE_PLIST_LV_INFO)
    corestorage.util.GetPlistFromExec(mox.In(DISKUTIL)).AndReturn(
        pl)
    self.mox.ReplayAll()
    self.assertEqual('55.00 GiB', corestorage.GetVolumeSize(mock_uuid))
    self.mox.VerifyAll()

  def testUnlockVolumeAlreadyUnlocked(self):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())
    self.mox.StubOutWithMock(corestorage.util, 'Exec')
    corestorage.util.Exec(
        mox.In(DISKUTIL), stdin=mock_passphrase).AndReturn(
            (1, '',
             'Error beginning CoreStorage Logical Volume unlock: '
             'The target Core Storage volume is not locked (-69748)'))
    self.mox.ReplayAll()
    corestorage.UnlockVolume(mock_uuid, mock_passphrase)
    self.mox.VerifyAll()

  def testUnlockVolumeCantUnlock(self):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())
    self.mox.StubOutWithMock(corestorage.util, 'Exec')
    corestorage.util.Exec(
        mox.In(DISKUTIL), stdin=mock_passphrase).AndReturn(
            (1, '', ''))
    self.mox.ReplayAll()
    self.assertRaises(corestorage.CouldNotUnlockError,
                      corestorage.UnlockVolume, mock_uuid, mock_passphrase)
    self.mox.VerifyAll()

  def testUnlockVolumeOk(self):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())
    self.mox.StubOutWithMock(corestorage.util, 'Exec')
    corestorage.util.Exec(
        mox.In(DISKUTIL), stdin=mock_passphrase).AndReturn(
            (0, '', ''))
    self.mox.ReplayAll()
    corestorage.UnlockVolume(mock_uuid, mock_passphrase)
    self.mox.VerifyAll()

  def testRevertVolumeCantRevert(self):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())
    self.mox.StubOutWithMock(corestorage, 'UnlockVolume')
    self.mox.StubOutWithMock(corestorage.util, 'Exec')
    corestorage.UnlockVolume(mock_uuid, mock_passphrase).AndReturn(None)
    corestorage.util.Exec(
        mox.In(DISKUTIL), stdin=mock_passphrase).AndReturn(
            (1, '', ''))
    self.mox.ReplayAll()
    self.assertRaises(corestorage.CouldNotRevertError,
                      corestorage.RevertVolume, mock_uuid, mock_passphrase)
    self.mox.VerifyAll()

  def testRevertVolumeOk(self):
    mock_uuid = str(uuid.uuid4())
    mock_passphrase = str(uuid.uuid4())
    self.mox.StubOutWithMock(corestorage, 'UnlockVolume')
    self.mox.StubOutWithMock(corestorage.util, 'Exec')
    corestorage.UnlockVolume(mock_uuid, mock_passphrase).AndReturn(None)
    corestorage.util.Exec(
        mox.In(DISKUTIL), stdin=mock_passphrase).AndReturn(
            (0, '', ''))
    self.mox.ReplayAll()
    corestorage.RevertVolume(mock_uuid, mock_passphrase)
    self.mox.VerifyAll()


if __name__ == '__main__':
  unittest.main()