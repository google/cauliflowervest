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

"""APFS related features (based on corestorage)."""

from cauliflowervest.client import util
from cauliflowervest.client.mac import storage


DISKUTIL = '/usr/sbin/diskutil'
FDESETUP = '/usr/bin/fdesetup'
APFS_ROLES = ['Preboot', 'Recovery', 'VM']


class State(object):
  """Fake enum to represent the possible states of APFS disk."""
  ENABLED = 'APFS_STATE_ENABLED'
  ENCRYPTED = 'APFS_STATE_ENCRYPTED'
  FAILED = 'APFS_STATE_FAILED'
  NONE = 'APFS_STATE_NONE'
  UNKNOWN = 'APFS_STATE_UNKNOWN'


class APFSStorage(storage.Storage):
  """Storage class for APFS disks."""

  def __init__(self):
    self._volumes = []
    self._containers = []

  def _GetAPFSVolumesAndContainers(self, uuid=None, disk=None):
    """Returns a tuple of volumes and containers from apfs list -plist.

    Args:
      uuid: str, optional, APFSVolume uuid. If no uuid is provided, this
            function returns a diskutil apfs list plist..
      disk: str, optional, name of the disk to look at.
    Returns:
      A dict of diskutil cs info/list -plist output.
    Raises:
      Error: The given uuid was invalid or there was a diskutil error.
    """
    if uuid:
      if not util.UuidIsValid(uuid):
        raise storage.Error

    if disk or not self._containers:
      cmd = [DISKUTIL, 'apfs', 'list', '-plist']
      if disk:
        cmd.append(disk)
      try:
        plist = util.GetPlistFromExec(cmd)
      except util.ExecError:
        return ([], [])
      containers = plist.get('Containers', [])
      if containers:
        volumes = containers[0].get('Volumes', [])
      else:
        volumes = []

      if not disk:   # save the full list for future lookups
        self._containers = containers
        self._volumes = volumes
    else:
      containers = self._containers
      volumes = self._volumes

    if uuid:
      uuid_volumes = []
      for volume in volumes:
        if volume.get('APFSVolumeUUID') == uuid:
          uuid_volumes.append(volume)
      return (uuid_volumes, containers)
    else:
      return (volumes, containers)

  def _GetAPFSVolumes(self, uuid=None, disk=None):
    (volumes, _) = self._GetAPFSVolumesAndContainers(uuid=uuid, disk=disk)
    return volumes

  def GetVolumeUUID(self, disk):
    (volumes, _) = self._GetAPFSVolumesAndContainers(disk=disk)
    if not volumes:
      return None
    return volumes[0].get('APFSVolumeUUID', None)

  def GetPrimaryVolumeUUID(self):
    """Returns string UUID of the boot volume (/), or None if error."""
    cmd = [DISKUTIL, 'info', '-plist', '/']
    try:
      plist = util.GetPlistFromExec(cmd)
    except util.ExecError:
      return None
    return plist.get('VolumeUUID')

  def IsBootVolumeEncrypted(self):
    """Returns True if the boot volume (/) is encrypted, False otherwise."""
    uuid = self.GetPrimaryVolumeUUID()
    if not uuid:
      return False
    volumes = self._GetAPFSVolumes(uuid=uuid)
    return bool(volumes and volumes[0].get('Encryption'))

  def GetRecoveryPartition(self):
    """Determine the location of the recovery partition.

    Returns:
      str, like "/dev/disk0s3" where the recovery partition is, OR
      None, if no recovery partition exists or cannot be detected.
    """
    volumes = self._GetAPFSVolumes()
    for volume in volumes:
      if volume.get('Name') == 'Recovery':
        return '/dev/%s' % volume.get('DeviceIdentifier')
    return None

  def GetStateAndVolumeIds(self):
    """Determine the state of APFS and the volume IDs (if any).

    In the case that APFS is enabled, it is required that every present
    volume is encrypted, to return "encrypted" status (i.e. the entire drive is
    encrypted, for all present drives).  Otherwise ENABLED or FAILED state is
    returned.

    Returns:
      tuple: (State, [list; str encrypted UUIDs], [list; str unencrypted UUIDs])
    Raises:
      Error: there was a problem getting the APFS list.
    """
    state = State.NONE
    volume_ids = []
    encrypted_volume_ids = []
    failed_volume_ids = []

    volumes = self._GetAPFSVolumes()
    if volumes:
      state = State.ENABLED
    for volume in volumes:
      volume_id = volume['APFSVolumeUUID']
      # roles can be '' (for HD), Preboot, Recovery, VM
      roles = volume.get('Roles')
      #  How do we detect failure?
      conv_state = volume.get('APFSVolumeConversionState', '')
      if conv_state == 'Failed':
        failed_volume_ids.append(volume_id)
      elif not roles or roles[0] not in APFS_ROLES:
        if volume.get('Encryption'):
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
    """Return the APFS state.

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
      raise storage.InvalidUUIDErrorError('Invalid UUID: ' + uuid)
    (volumes, containers) = self._GetAPFSVolumesAndContainers(uuid)

    num_bytes = 0
    for volume in volumes:
      if volume.get('APFSVolumeUUID') == uuid:
        num_bytes = (containers[0].get('CapacityFree') +
                     volume.get('CapacityInUse'))
        break

    if readable:
      return '%.2f GiB' % (num_bytes / (1<<30))
    else:
      return num_bytes

  def UnlockVolume(self, uuid, passphrase):
    """Unlock an APFS encrypted volume.

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
        (DISKUTIL, 'apfs', 'unlockVolume', uuid, '-stdinpassphrase'),
        stdin=passphrase)
    if (returncode != 0 and
        'volume is not locked' not in stderr and
        'is already unlocked' not in stderr):
      raise storage.CouldNotUnlockError(
          'Could not unlock volume (%s).' % returncode)

  def RevertVolume(self, uuid, passphrase, passwd=''):
    """Disable encryption on an APFS system.

    Args:
      uuid: str, uuid of the volume to revert.
      passphrase: str, passphrase to unlock the volume.
      passwd: str, password for sudo
    Raises:
      CouldNotRevertError: the volume was unlocked, but cannot be reverted.
      CouldNotUnlockError: the volume cannot be unlocked.
      InvalidUUIDError: The UUID is formatted incorrectly.
    """
    if not util.UuidIsValid(uuid):
      raise storage.InvalidUUIDError('Invalid UUID: ' + uuid)
    self.UnlockVolume(uuid, passphrase)
    returncode, _, _ = util.Exec(
        ('sudo', '-k', '-S', FDESETUP, 'disable'),
        stdin=passwd+'\n')

    if returncode != 0:
      raise storage.CouldNotRevertError('Could not disable encryption (%s).' % (
          returncode))
