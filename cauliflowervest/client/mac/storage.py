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

"""Abstract base class for different storage types."""

from abc import abstractmethod


class Error(Exception):
  """Base error."""


class CouldNotUnlockError(Error):
  """Could not unlock volume error."""


class CouldNotRevertError(Error):
  """Could not revert volume error."""


class VolumeNotEncryptedError(Error):
  """Volume is not encrypted error."""


class InvalidUUIDError(Error):
  """Volume UUID is formatted incorrectly."""


class Storage(object):
  """abstract base class for Storage types."""

  @abstractmethod
  def IsBootVolumeEncrypted(self):
    raise NotImplementedError

  @abstractmethod
  def GetRecoveryPartition(self):
    raise NotImplementedError

  @abstractmethod
  def GetStateAndVolumeIds(self):
    raise NotImplementedError

  @abstractmethod
  def GetPrimaryVolumeUUID(self):
    raise NotImplementedError

  @abstractmethod
  def GetState(self):
    raise NotImplementedError

  @abstractmethod
  def GetVolumeSize(self, volume):
    raise NotImplementedError

  @abstractmethod
  def RevertVolume(self, volume_uuid, passphrase, passwd):
    raise NotImplementedError

  @abstractmethod
  def UnlockVolume(self, volume_uuid, passphrase):
    raise NotImplementedError
