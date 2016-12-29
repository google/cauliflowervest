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
"""Models related to Volume Encryption."""
import datetime

from google.appengine.ext import db

from cauliflowervest import settings as base_settings
from cauliflowervest.server.models import base


# can be used by crypto backend as key name.
# so should never change.
_PROVISIONING_PASSPHRASE_ENCRYPTION_KEY_NAME = 'provisioning'
_LUKS_PASSPHRASE_ENCRYPTION_KEY_NAME = 'luks'
_DUPLICITY_KEY_PAIR_ENCRYPTION_KEY_NAME = 'duplicity'
_BITLOCKER_PASSPHRASE_ENCRYPTION_KEY_NAME = 'bitlocker'
_FILEVAULT_PASSPHRASE_ENCRYPTION_KEY_NAME = 'filevault'


class BitLockerAccessError(base.AccessError):
  """There was an error accessing a BitLocker key."""


class DuplicityAccessError(base.AccessError):
  """There was an error accessing a Duplicity key pair."""


class FileVaultAccessError(base.AccessError):
  """There was an error accessing a FileVault passphrase."""


class LuksAccessError(base.AccessError):
  """There was an error accessing a Luks passphrase."""


class ProvisioningAccessError(base.AccessError):
  """There was an error accessing a Provisioning passphrase."""


class BitLockerAccessLog(base.AccessLog):
  """Model for logging access to BitLocker keys."""


class DuplicityAccessLog(base.AccessLog):
  """Model for logging access to Duplicity key pairs."""


class FileVaultAccessLog(base.AccessLog):
  """Model for logging access to FileVault passphrases."""


class LuksAccessLog(base.AccessLog):
  """Model for logging access to Luks passphrases."""


class ProvisioningAccessLog(base.AccessLog):
  """Model for logging access to Provisioning passphrases."""


class FileVaultVolume(base.BaseVolume):
  """Model for storing FileVault Volume passphrases, with various metadata."""

  ACCESS_ERR_CLS = FileVaultAccessError
  ESCROW_TYPE_NAME = 'filevault'
  REQUIRED_PROPERTIES = base_settings.FILEVAULT_REQUIRED_PROPERTIES + [
      'passphrase', 'volume_uuid']
  SEARCH_FIELDS = [
      ('owner', 'Owner Username'),
      ('created_by', 'Escrow Username'),
      ('hdd_serial', 'Hard Drive Serial Number'),
      ('hostname', 'Hostname'),
      ('serial', 'Machine Serial Number'),
      ('platform_uuid', 'Platform UUID'),
      ('volume_uuid', 'Volume UUID'),
      ]
  SECRET_PROPERTY_NAME = 'passphrase'
  ALLOW_OWNER_CHANGE = True

  # NOTE(user): For self-service encryption, owner/created_by may the same.
  #   Furthermore, created_by may go away if we implement unattended encryption
  #   via machine/certificate-based auth.
  passphrase = base.EncryptedBlobProperty(
      _FILEVAULT_PASSPHRASE_ENCRYPTION_KEY_NAME)
  platform_uuid = db.StringProperty()  # sp_platform_uuid in facter.
  serial = db.StringProperty()  # serial number of the machine.
  hdd_serial = db.StringProperty()  # hard drive disk serial number.

  @classmethod
  def NormalizeHostname(cls, hostname):
    """Ensures hostname is non-fully qualified and lowercased."""
    return super(FileVaultVolume, cls).NormalizeHostname(
        hostname, strip_fqdn=True)


class BitLockerVolume(base.BaseVolume):
  """Model for storing BitLocker Volume keys."""

  ACCESS_ERR_CLS = BitLockerAccessError
  ESCROW_TYPE_NAME = 'bitlocker'
  REQUIRED_PROPERTIES = [
      'dn', 'hostname', 'parent_guid', 'recovery_key', 'volume_uuid'
  ]
  SEARCH_FIELDS = [
      ('hostname', 'Hostname'),
      ('volume_uuid', 'Volume UUID'),
      ]
  SECRET_PROPERTY_NAME = 'recovery_key'

  recovery_key = base.EncryptedBlobProperty(
      _BITLOCKER_PASSPHRASE_ENCRYPTION_KEY_NAME)
  dn = db.StringProperty()
  parent_guid = db.StringProperty()
  when_created = db.DateTimeProperty()

  @classmethod
  def NormalizeHostname(cls, hostname):
    """Ensures hostname is non-fully qualified and lowercased."""
    return super(BitLockerVolume, cls).NormalizeHostname(
        hostname, strip_fqdn=True).upper()



class DuplicityKeyPair(base.BaseVolume):
  """Model for storing Duplicity key pairs."""

  ACCESS_ERR_CLS = DuplicityAccessError
  ESCROW_TYPE_NAME = 'duplicity'
  REQUIRED_PROPERTIES = base_settings.DUPLICITY_REQUIRED_PROPERTIES + [
      'key_pair',
      'owner',
      'volume_uuid',
      ]
  SECRET_PROPERTY_NAME = 'key_pair'

  platform_uuid = db.StringProperty()
  key_pair = base.EncryptedBlobProperty(_DUPLICITY_KEY_PAIR_ENCRYPTION_KEY_NAME)


class LuksVolume(base.BaseVolume):
  """Model for storing Luks passphrases."""

  ACCESS_ERR_CLS = LuksAccessError
  ESCROW_TYPE_NAME = 'luks'
  REQUIRED_PROPERTIES = base_settings.LUKS_REQUIRED_PROPERTIES + [
      'passphrase',
      'hostname',
      'platform_uuid',
      'owner',
      'volume_uuid',
      ]
  SEARCH_FIELDS = [
      ('owner', 'Device Owner'),
      ('hostname', 'Hostname'),
      ('volume_uuid', 'Volume UUID'),
      ('created_by', 'Escrow Username'),
      ('platform_uuid', 'MrMagoo Host UUID'),
      ('hdd_serial', 'Hard Drive Serial Number'),
      ]
  SECRET_PROPERTY_NAME = 'passphrase'

  passphrase = base.EncryptedBlobProperty(_LUKS_PASSPHRASE_ENCRYPTION_KEY_NAME)
  hdd_serial = db.StringProperty()
  platform_uuid = db.StringProperty()


class ProvisioningVolume(base.BaseVolume):
  """Model for storing Provisioning Volume passphrases."""

  ACCESS_ERR_CLS = ProvisioningAccessError
  ESCROW_TYPE_NAME = 'provisioning'
  REQUIRED_PROPERTIES = base_settings.PROVISIONING_REQUIRED_PROPERTIES + [
      'passphrase', 'volume_uuid']
  SEARCH_FIELDS = [
      ('owner', 'Owner Username'),
      ('created_by', 'Escrow Username'),
      ('hdd_serial', 'Hard Drive Serial Number'),
      ('hostname', 'Hostname'),
      ('serial', 'Machine Serial Number'),
      ('platform_uuid', 'Platform UUID'),
      ('volume_uuid', 'Volume UUID'),
      ]
  SECRET_PROPERTY_NAME = 'passphrase'

  # NOTE(user): For self-service encryption, owner/created_by may the same.
  #   Furthermore, created_by may go away if we implement unattended encryption
  #   via machine/certificate-based auth.
  passphrase = base.EncryptedBlobProperty(
      _PROVISIONING_PASSPHRASE_ENCRYPTION_KEY_NAME)
  platform_uuid = db.StringProperty()  # sp_platform_uuid in facter.
  serial = db.StringProperty()  # serial number of the machine.
  hdd_serial = db.StringProperty()  # hard drive disk serial number.

  @classmethod
  def NormalizeHostname(cls, hostname):
    """Ensures hostname is non-fully qualified and lowercased."""
    return super(ProvisioningVolume, cls).NormalizeHostname(
        hostname, strip_fqdn=True)
