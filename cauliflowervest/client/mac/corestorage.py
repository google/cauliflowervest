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

"""Core storage related features."""

import logging

from cauliflowervest.client import util
from cauliflowervest.client.mac import storage


DISKUTIL = '/usr/sbin/diskutil'


class State(object):
  """Fake enum to represent the possible states of core storage."""
  ENABLED = 'CORE_STORAGE_STATE_ENABLED'
  ENCRYPTED = 'CORE_STORAGE_STATE_ENCRYPTED'
  FAILED = 'CORE_STORAGE_STATE_FAILED'
  NONE = 'CORE_STORAGE_STATE_NONE'
  UNKNOWN = 'CORE_STORAGE_STATE_UNKNOWN'


class CoreStorage(storage.Storage):
  """Storage class for CoreStorage disks."""

  def IsBootVolumeEncrypted(self):
    """Returns True if the boot volume (/) is encrypted, False otherwise."""
    try:
      csinfo_plist = util.GetPlistFromExec(
          (DISKUTIL, 'cs', 'info', '-plist', '/'))
    except util.ExecError:
      return False  # Non-zero return means / volume isn't a CoreStorage volume.

    lvf_uuid = csinfo_plist.get('MemberOfCoreStorageLogicalVolumeFamily')
    if lvf_uuid:
      try:
        lvf_info_plist = util.GetPlistFromExec(
            (DISKUTIL, 'cs', 'info', '-plist', lvf_uuid))
      except util.ExecError:
        return False  # Couldn't get info on Logical Volume Family UUID.
      return lvf_info_plist.get(
          'CoreStorageLogicalVolumeFamilyEncryptionType') == 'AES-XTS'

    return False

  def GetRecoveryPartition(self):
    """Determine the location of the recovery partition.

    Returns:
      str, like "/dev/disk0s3" where the recovery partition is, OR
      None, if no recovery partition exists or cannot be detected.
    """
    try:
      disklist_plist = util.GetPlistFromExec((DISKUTIL, 'list', '-plist'))
    except util.ExecError:
      logging.exception('GetRecoveryPartition() failed to get partition list.')
      return

    alldisks = disklist_plist.get('AllDisksAndPartitions', [])
    for disk in alldisks:
      partitions = disk.get('Partitions', [])
      for partition in partitions:
        if partition.get('VolumeName') == 'Recovery HD':
          return '/dev/%s' % partition['DeviceIdentifier']

  def _GetCoreStoragePlist(self, uuid=None):
    """Returns a dict of diskutil cs info plist for a given CoreStorage uuid.

    Args:
      uuid: str, optional, CoreStorage uuid. If no uuid is provided, this
            function returns a diskutil cs list plist..
    Returns:
      A dict of diskutil cs info/list -plist output.
    Raises:
      Error: The given uuid was invalid or there was a diskutil error.
    """
    if uuid:
      if not util.UuidIsValid(uuid):
        raise storage.Error
      cmd = [DISKUTIL, 'corestorage', 'info', '-plist', uuid]
    else:
      cmd = [DISKUTIL, 'corestorage', 'list', '-plist']
    try:
      return util.GetPlistFromExec(cmd)
    except util.ExecError as e:
      logging.error('Error in execing %s: %s', cmd, e)
      raise storage.Error

  def GetPrimaryVolumeUUID(self):
    state, encrypted_uuids, unencrypted_uuids = self.GetStateAndVolumeIds()
    uuid = None
    if state == State.ENCRYPTED or state == State.ENABLED:
      if encrypted_uuids:
        uuid = encrypted_uuids[0]
    else:
      if unencrypted_uuids:
        uuid = unencrypted_uuids[0]
    return uuid

  def GetStateAndVolumeIds(self):
    """Determine the state of core storage and the volume IDs (if any).

    In the case that core storage is enabled, it is required that every present
    volume is encrypted, to return "encrypted" status (i.e. the entire drive is
    encrypted, for all present drives).  Otherwise ENABLED or FAILED state is
    returned.

    Returns:
      tuple: (State, [list; str encrypted UUIDs], [list; str unencrypted UUIDs])
    Raises:
      Error: there was a problem getting the corestorage list, or family info.
    """
    state = State.NONE
    volume_ids = []
    encrypted_volume_ids = []
    failed_volume_ids = []

    cs_plist = self._GetCoreStoragePlist()
    groups = cs_plist.get('CoreStorageLogicalVolumeGroups', [])
    if groups:
      state = State.ENABLED
    for group in groups:
      for family in group.get('CoreStorageLogicalVolumeFamilies', []):
        family_plist = self._GetCoreStoragePlist(family['CoreStorageUUID'])
        enc = family_plist.get('CoreStorageLogicalVolumeFamilyEncryptionType',
                               '')
        for volume in family['CoreStorageLogicalVolumes']:
          volume_id = volume['CoreStorageUUID']
          volume_plist = self._GetCoreStoragePlist(volume_id)
          conv_state = volume_plist.get(
              'CoreStorageLogicalVolumeConversionState', '')
          # Known states include: Pending, Converting, Complete, Failed.
          if conv_state == 'Failed':
            failed_volume_ids.append(volume_id)
          elif enc == 'AES-XTS':
            # If conv_state is not 'Failed' and enc is correct, consider the
            # volume encrypted to include those that are still encrypting.
            # A potential TODO might be to separate these.
            encrypted_volume_ids.append(volume_id)
          else:
            volume_ids.append(volume_id)

    if failed_volume_ids:
      state = State.FAILED
    elif encrypted_volume_ids and not volume_ids:
      state = State.ENCRYPTED

    # For now at least, consider "failed" volumes as encrypted, as the same
    # actions are valid for such volumes. For example: revert.
    encrypted_volume_ids.extend(failed_volume_ids)

    return state, encrypted_volume_ids, volume_ids

  def GetState(self):
    """Check if core storage is in place.

    Returns:
      One of the class properties of State.
    """
    state, _, _ = self.GetStateAndVolumeIds()
    return state

  def GetVolumeSize(self, uuid, readable=True):
    """Return the size of the volume with the given UUID.

    Args:
      uuid: str, ID of the volume in question
      readable: Optional boolean, default true: return a human-readable string
        when true, otherwise int number of bytes.

    Returns:
      str or int, see "readable" arg.
    Raises:
      Error: there was a problem getting volume info.
      InvalidUUIDError: The UUID is formatted incorrectly.
    """
    if not util.UuidIsValid(uuid):
      raise storage.InvalidUUIDError('Invalid UUID: ' + uuid)
    try:
      plist = util.GetPlistFromExec(
          (DISKUTIL, 'corestorage', 'info', '-plist', uuid))
    except util.ExecError:
      logging.exception('GetVolumeSize() failed to get volume info: %s', uuid)
      raise storage.Error

    num_bytes = plist['CoreStorageLogicalVolumeSize']
    if readable:
      return '%.2f GiB' % (num_bytes / (1<<30))
    else:
      return num_bytes

  def UnlockVolume(self, uuid, passphrase):
    """Unlock a core storage encrypted volume.

    Args:
      uuid: str, uuid of the volume to unlock.
      passphrase: str, passphrase to unlock the volume.
    Raises:
      CouldNotUnlockError: the volume cannot be unlocked.
      InvalidUUIDError: The UUID is formatted incorrectly.
    """
    if not util.UuidIsValid(uuid):
      raise storage.InvalidUUIDError('Invalid UUID: ' + uuid)
    returncode, _, stderr = util.Exec(
        (DISKUTIL, 'corestorage', 'unlockVolume', uuid, '-stdinpassphrase'),
        stdin=passphrase)
    if (returncode != 0 and
        'volume is not locked' not in stderr and
        'is already unlocked' not in stderr):
      raise storage.CouldNotUnlockError(
          'Could not unlock volume (%s).' % returncode)

  def RevertVolume(self, uuid, passphrase, unused_passwd=''):
    """Revert a core storage encrypted volume (to unencrypted state).

    Args:
      uuid: str, uuid of the volume to revert.
      passphrase: str, passphrase to unlock the volume.
      unused_passwd: str, password for sudo
    Raises:
      CouldNotRevertError: the volume was unlocked, but cannot be reverted.
      CouldNotUnlockError: the volume cannot be unlocked.
      InvalidUUIDError: The UUID is formatted incorrectly.
    """
    if not util.UuidIsValid(uuid):
      raise storage.InvalidUUIDError('Invalid UUID: ' + uuid)
    self.UnlockVolume(uuid, passphrase)
    returncode, _, _ = util.Exec(
        (DISKUTIL, 'corestorage', 'revert', uuid, '-stdinpassphrase'),
        stdin=passphrase)
    if returncode != 0:
      raise storage.CouldNotRevertError(
          'Could not revert volume (%s).' % returncode)
