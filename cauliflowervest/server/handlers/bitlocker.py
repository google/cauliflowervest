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

"""Module to handle interaction with a BitLocker."""

import datetime
import logging

from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server.handlers import passphrase_handler
from cauliflowervest.server.models import base
from cauliflowervest.server.models import volumes as models


class BitLocker(passphrase_handler.PassphraseHandler):
  """Handler for /bitlocker URL."""
  AUDIT_LOG_MODEL = models.BitLockerAccessLog
  SECRET_MODEL = models.BitLockerVolume
  PERMISSION_TYPE = permissions.TYPE_BITLOCKER


  def get(self, volume_uuid=None):
    """Handles GET requests."""
    if volume_uuid is not None:
      volume_uuid = volume_uuid.upper()
    super(BitLocker, self).get(volume_uuid)

  def _CreateNewSecretEntity(self, unused_owner, volume_uuid, secret):
    return models.BitLockerVolume(
        volume_uuid=volume_uuid,
        recovery_key=str(secret))

  def SanitizeEntityValue(self, prop_name, value):
    if prop_name == 'when_created':
      value = value.strip()
      try:
        return datetime.datetime.strptime(value, '%Y%m%d%H%M%S.0Z')
      except ValueError:
        logging.error('Unknown when_created format: %r', value)
        return None
    return super(BitLocker, self).SanitizeEntityValue(prop_name, value)
