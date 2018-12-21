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

"""Models related to Backup Encryption."""

from google.appengine.ext import db

from cauliflowervest import settings as base_settings
from cauliflowervest.server import encrypted_property
from cauliflowervest.server import services
from cauliflowervest.server.models import base
from cauliflowervest.server.models import errors


# Can be used by crypto backend as key name,
# so should never change.
_DUPLICITY_KEY_PAIR_ENCRYPTION_KEY_NAME = 'duplicity'


class DuplicityAccessError(errors.AccessError):
  """There was an error accessing a Duplicity key pair."""


class DuplicityAccessLog(base.AccessLog):
  """Model for logging access to Duplicity key pairs."""


class DuplicityKeyPair(base.BasePassphrase,
                       services.InventoryServiceBackupPassphraseProperties):
  """Model for storing Duplicity key pairs.

  Duplicity backups are assosiated with user and not machine.
  http://duplicity.nongnu.org/
  """

  ACCESS_ERR_CLS = DuplicityAccessError
  AUDIT_LOG_MODEL = DuplicityAccessLog
  ESCROW_TYPE_NAME = 'duplicity'
  REQUIRED_PROPERTIES = base_settings.DUPLICITY_REQUIRED_PROPERTIES + [
      'key_pair',
      'owners',
      'volume_uuid',
  ]
  MUTABLE_PROPERTIES = (
      base.BasePassphrase.MUTABLE_PROPERTIES +
      services.InventoryServiceBackupPassphraseProperties.MUTABLE_PROPERTIES)
  SEARCH_FIELDS = [
      ('owner', 'Owner Username'),
      ('hostname', 'Hostname'),
  ]
  SECRET_PROPERTY_NAME = 'key_pair'
  TARGET_PROPERTY_NAME = 'volume_uuid'

  platform_uuid = db.StringProperty()
  key_pair = encrypted_property.EncryptedBlobProperty(
      _DUPLICITY_KEY_PAIR_ENCRYPTION_KEY_NAME)

  volume_uuid = db.StringProperty()  # UUID of the backup.
