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

"""Models related to Firmware Encryption."""

from google.appengine.ext import db

from cauliflowervest.server import encrypted_property
from cauliflowervest.server.models import base
from cauliflowervest.server.models import errors


_APPLE_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME = 'apple_firmware'
_LINUX_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME = 'linux_firmware'
_WINDOWS_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME = 'windows_firmware'


class _BaseFirmwarePassword(base.BasePassphrase):
  """Base class for Firmware models."""
  ACCESS_ERR_CLS = errors.AccessError
  ALLOW_OWNER_CHANGE = True

  asset_tags = db.StringListProperty()

  def ToDict(self, skip_secret=False):
    o = super(_BaseFirmwarePassword, self).ToDict(skip_secret)
    o['asset_tags'] = ', '.join(self.asset_tags)
    return o


class AppleFirmwarePasswordAccessLog(base.AccessLog):
  """Model for logging access to Apple Firmware passwords."""


class AppleFirmwarePassword(_BaseFirmwarePassword):
  """Model for storing Apple Firmware passwords, with various metadata."""
  AUDIT_LOG_MODEL = AppleFirmwarePasswordAccessLog
  TARGET_PROPERTY_NAME = 'serial'
  ESCROW_TYPE_NAME = 'apple_firmware'
  SECRET_PROPERTY_NAME = 'password'

  REQUIRED_PROPERTIES = [
      'platform_uuid', 'password', 'hostname', 'serial',
  ]
  SEARCH_FIELDS = [
      ('asset_tags', 'Asset Tag'),
      ('hostname', 'Hostname'),
      ('serial', 'Machine Serial Number'),
      ('platform_uuid', 'Platform UUID'),
  ]

  password = encrypted_property.EncryptedBlobProperty(
      _APPLE_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME)

  serial = db.StringProperty()
  platform_uuid = db.StringProperty()  # sp_platform_uuid in facter.


class LinuxFirmwarePasswordAccessLog(base.AccessLog):
  """Model for logging access to Linux Firmware passwords."""


class LinuxFirmwarePassword(_BaseFirmwarePassword):
  """Model for storing Linux Firmware passwords, with various metadata."""
  AUDIT_LOG_MODEL = LinuxFirmwarePasswordAccessLog
  TARGET_PROPERTY_NAME = '_manufacturer_serial_machine_uuid'
  ESCROW_TYPE_NAME = 'linux_firmware'
  SECRET_PROPERTY_NAME = 'password'

  REQUIRED_PROPERTIES = [
      'manufacturer', 'serial', 'password', 'hostname', 'machine_uuid'
  ]
  SEARCH_FIELDS = [
      ('asset_tags', 'Asset Tag'),
      ('hostname', 'Hostname'),
      ('manufacturer', 'Machine Manufacturer'),
      ('serial', 'Machine Serial Number'),
      ('machine_uuid', 'Machine UUID'),
  ]

  password = encrypted_property.EncryptedBlobProperty(
      _LINUX_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME)

  manufacturer = db.StringProperty()  # /sys/class/dmi/id/sys_vendor.
  serial = db.StringProperty()  # /sys/class/dmi/id/product_serial.
  machine_uuid = db.StringProperty()  # /sys/class/dmi/id/product_uuid.
  _manufacturer_serial_machine_uuid = db.ComputedProperty(
      lambda self: self.manufacturer + self.serial + self.machine_uuid)


class WindowsFirmwarePasswordAccessLog(base.AccessLog):
  """Model for logging access to Windows Firmware passwords."""


class WindowsFirmwarePassword(_BaseFirmwarePassword):
  """Model for storing Windows Firmware passwords, with various metadata."""
  AUDIT_LOG_MODEL = WindowsFirmwarePasswordAccessLog
  TARGET_PROPERTY_NAME = 'serial'
  ESCROW_TYPE_NAME = 'windows_firmware'
  SECRET_PROPERTY_NAME = 'password'

  REQUIRED_PROPERTIES = [
      'serial', 'password', 'hostname', 'smbios_guid'
  ]
  SEARCH_FIELDS = [
      ('asset_tags', 'Asset Tag'),
      ('hostname', 'Hostname'),
      ('serial', 'Machine Serial Number'),
      ('smbios_guid', 'SMBIOS UUID'),
  ]

  password = encrypted_property.EncryptedBlobProperty(
      _WINDOWS_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME)

  # serial from WMI query: 'Select SerialNumber from Win32_BIOS'
  serial = db.StringProperty()
  # smbios_guid from WMI query: 'Select UUID from Win32_ComputerSystemProduct'
  smbios_guid = db.StringProperty()
