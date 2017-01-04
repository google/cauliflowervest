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
"""Module to handle interaction with a Provisioning Password."""

import re

from cauliflowervest.server import handlers
from cauliflowervest.server import permissions
from cauliflowervest.server import util
from cauliflowervest.server.models import base
from cauliflowervest.server.models import volumes as models


class Provisioning(handlers.AccessHandler):
  """Handler for /provisioning URL."""
  AUDIT_LOG_MODEL = models.ProvisioningAccessLog
  SECRET_MODEL = models.ProvisioningVolume
  PERMISSION_TYPE = permissions.TYPE_PROVISIONING

  UUID_REGEX = re.compile(r'^[0-9A-Z\-]+$')

  # We don't want to display barcodes for users retrieving provisioning
  # passwords as seeing the barcodes frightens and confuses them.
  QRCODE_DURING_PASSPHRASE_RETRIEVAL = False

  def _PassphraseTypeName(self, _):
    return 'Temporary password'

  def _CreateNewSecretEntity(self, owner, volume_uuid, secret):
    user = base.GetCurrentUser()
    platform = self.request.get('platform')
    # Set default platform to Mac
    if not platform:
      platform = 'Mac'


    return models.ProvisioningVolume(
        owner=owner,
        volume_uuid=volume_uuid,
        passphrase=str(secret))
