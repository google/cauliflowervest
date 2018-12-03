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

"""Base class for interactions with Firmware Passwords."""

import logging
import re

from cauliflowervest import settings as base_settings
from cauliflowervest.server import service_factory
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.handlers import passphrase_handler
from cauliflowervest.server.models import base
from cauliflowervest.server.models import errors


class FirmwarePasswordHandler(passphrase_handler.PassphraseHandler):
  """Base class for handler firmware password upload/retrieval."""
  TARGET_ID_REGEX = re.compile(r'^[0-9A-Z\-]+$')
  #  Increase SECRET_REGEX mimimum character limit to 5.
  SECRET_REGEX = re.compile(r'^[a-zA-Z0-9]{3,15}$')

  def _VerifyEscrowPermission(self):
    try:
      base.GetCurrentUser()
    except errors.AccessDeniedError:
      pass
    else:
      return super(FirmwarePasswordHandler, self)._VerifyEscrowPermission()
    raise errors.AccessDeniedError

  def _CreateNewSecretEntity(self, owner, target_id, secret):
    entity = self.SECRET_MODEL(
        owner=owner,
        serial=target_id,
        password=str(secret))

    secret_len = len(str(secret))
    if secret_len < 5:
      logging.info('Firmware password < 5 letters escrowed. '
                   'Length of secret: %d', secret_len)

    inventory = service_factory.GetInventoryService()
    entity.asset_tags = inventory.GetAssetTagsFromUploadRequest(
        entity, self.request)

    return entity


  def IsValidSecret(self, secret):
    """Returns true if secret str is a well formatted."""
    return self.SECRET_REGEX.match(secret) is not None

  def Publish(self, _):
    pass
