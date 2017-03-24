#!/usr/bin/env python
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
"""Models related to Firmware Encryption."""

from google.appengine.ext import db

from cauliflowervest.server import encrypted_property
from cauliflowervest.server.models import base

_APPLE_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME = 'apple_firmware'
_DELL_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME = 'dell_firmware'
_HP_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME = 'hp_firmware'
_LENOVO_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME = 'lenovo_firmware'


class AppleFirmwarePassword(base.BasePassphrase):
  """Model for storing Apple Firmware passwords, with various metadata."""
  TARGET_PROPERTY_NAME = 'serial'
  ESCROW_TYPE_NAME = 'apple_firmware'
  SECRET_PROPERTY_NAME = 'password'

  REQUIRED_PROPERTIES = [
      'platform_uuid', 'password', 'hostname', 'serial',
  ]
  SEARCH_FIELDS = [
      ('hostname', 'Hostname'),
      ('serial', 'Machine Serial Number'),
      ('platform_uuid', 'Platform UUID'),
  ]

  ACCESS_ERR_CLS = base.AccessError

  password = encrypted_property.EncryptedBlobProperty(
      _APPLE_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME)

  serial = db.StringProperty()
  platform_uuid = db.StringProperty()  # sp_platform_uuid in facter.


class DellFirmwarePassword(base.BasePassphrase):
  """Model for storing Dell Firmware passwords, with various metadata."""
  TARGET_PROPERTY_NAME = 'serial'
  ESCROW_TYPE_NAME = 'dell_firmware'
  SECRET_PROPERTY_NAME = 'password'

  REQUIRED_PROPERTIES = [
      'serial', 'password', 'hostname',
  ]
  ACCESS_ERR_CLS = base.AccessError

  password = encrypted_property.EncryptedBlobProperty(
      _DELL_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME)
  serial = db.StringProperty()


class HpFirmwarePassword(base.BasePassphrase):
  """Model for storing HP Firmware passwords, with various metadata."""
  TARGET_PROPERTY_NAME = 'serial'
  ESCROW_TYPE_NAME = 'hp_firmware'
  SECRET_PROPERTY_NAME = 'password'

  REQUIRED_PROPERTIES = [
      'serial', 'password', 'hostname',
  ]
  ACCESS_ERR_CLS = base.AccessError

  password = encrypted_property.EncryptedBlobProperty(
      _HP_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME)
  serial = db.StringProperty()


class LenovoFirmwarePassword(base.BasePassphrase):
  """Model for storing Lenovo Firmware passwords, with various metadata."""
  TARGET_PROPERTY_NAME = 'serial'
  ESCROW_TYPE_NAME = 'lenovo_firmware'
  SECRET_PROPERTY_NAME = 'password'

  REQUIRED_PROPERTIES = [
      'serial', 'password', 'hostname',
  ]
  ACCESS_ERR_CLS = base.AccessError

  password = encrypted_property.EncryptedBlobProperty(
      _LENOVO_FIRMWARE_PASSWORD_ENCRYPTION_KEY_NAME)
  serial = db.StringProperty()


class AppleFirmwarePasswordAccessLog(base.AccessLog):
  """Model for logging access to Apple Firmware passwords."""


class DellFirmwarePasswordAccessLog(base.AccessLog):
  """Model for logging access to Dell Firmware passwords."""


class HpFirmwarePasswordAccessLog(base.AccessLog):
  """Model for logging access to HP Firmware passwords."""


class LenovoFirmwarePasswordAccessLog(base.AccessLog):
  """Model for logging access to Lenovo Firmware passwords."""
