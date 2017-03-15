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
"""Module to handle interaction with a Luks key."""

from cauliflowervest.server import permissions
from cauliflowervest.server.handlers import passphrase_handler
from cauliflowervest.server.models import volumes


class Luks(passphrase_handler.PassphraseHandler):
  """Handler for /luks URL."""
  AUDIT_LOG_MODEL = volumes.LuksAccessLog
  SECRET_MODEL = volumes.LuksVolume
  PERMISSION_TYPE = permissions.TYPE_LUKS

  def _CreateNewSecretEntity(self, owner, volume_uuid, secret):
    return volumes.LuksVolume(
        owner=owner,
        volume_uuid=volume_uuid,
        passphrase=str(secret))
