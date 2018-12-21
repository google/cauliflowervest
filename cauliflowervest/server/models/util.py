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

"""Common utilities."""
from cauliflowervest.server.models import backups
from cauliflowervest.server.models import firmware
from cauliflowervest.server.models import volumes


def AllModels():
  """Return all defined models."""
  return [
      volumes.FileVaultVolume, volumes.BitLockerVolume,
      backups.DuplicityKeyPair, volumes.LuksVolume,
      volumes.ProvisioningVolume, firmware.AppleFirmwarePassword,
      firmware.LinuxFirmwarePassword, firmware.WindowsFirmwarePassword,
  ]


def TypeNameToModel(type_name):
  """Return model with given type_name."""
  for model in AllModels():
    if model.ESCROW_TYPE_NAME == type_name:
      return model

  raise ValueError


def TypeNameToLogModel(type_name):
  """Return log model associated with type_name."""
  if type_name == volumes.BitLockerVolume.ESCROW_TYPE_NAME:
    return volumes.BitLockerAccessLog
  elif type_name == backups.DuplicityKeyPair.ESCROW_TYPE_NAME:
    return backups.DuplicityAccessLog
  elif type_name == volumes.FileVaultVolume.ESCROW_TYPE_NAME:
    return volumes.FileVaultAccessLog
  elif type_name == volumes.LuksVolume.ESCROW_TYPE_NAME:
    return volumes.LuksAccessLog
  elif type_name == volumes.ProvisioningVolume.ESCROW_TYPE_NAME:
    return volumes.ProvisioningAccessLog
  elif type_name == firmware.AppleFirmwarePassword.ESCROW_TYPE_NAME:
    return firmware.AppleFirmwarePasswordAccessLog
  elif type_name == firmware.LinuxFirmwarePassword.ESCROW_TYPE_NAME:
    return firmware.LinuxFirmwarePasswordAccessLog
  elif type_name == firmware.WindowsFirmwarePassword.ESCROW_TYPE_NAME:
    return firmware.WindowsFirmwarePasswordAccessLog

  raise ValueError
