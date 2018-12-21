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

"""Module for handling Duplicity GPG key pairs."""

import re

from cauliflowervest.server import permissions
from cauliflowervest.server.handlers import passphrase_handler
from cauliflowervest.server.models import backups


class Duplicity(passphrase_handler.PassphraseHandler):
  """Handler for /duplicity URL."""
  AUDIT_LOG_MODEL = backups.DuplicityAccessLog
  SECRET_MODEL = backups.DuplicityKeyPair
  PERMISSION_TYPE = permissions.TYPE_DUPLICITY

  JSON_SECRET_NAME = 'key_pair'
  TARGET_ID_REGEX = re.compile(r'^[a-f0-9]{32}$')

  def _CreateNewSecretEntity(self, owner, volume_uuid, secret):
    return backups.DuplicityKeyPair(
        key_pair=str(secret),
        owner=owner,
        volume_uuid=volume_uuid)


  def RetrieveSecret(self, volume_uuid):
    """Handles a GET request to retrieve a key pair."""
    self.request.json = '1'
    return super(Duplicity, self).RetrieveSecret(volume_uuid)
