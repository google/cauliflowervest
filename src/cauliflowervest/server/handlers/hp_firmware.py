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
"""Module to handle interactions with Hp Firmware Passwords."""

import re

from cauliflowervest import settings as base_settings
from cauliflowervest.server import permissions
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.handlers import passphrase_handler
from cauliflowervest.server.models import base
from cauliflowervest.server.models import firmware


class HpFirmwarePassword(passphrase_handler.PassphraseHandler):
  """Handler for /hp_firmware URL."""
  AUDIT_LOG_MODEL = firmware.HpFirmwarePasswordAccessLog
  SECRET_MODEL = firmware.HpFirmwarePassword
  PERMISSION_TYPE = permissions.TYPE_HP_FIRMWARE

  TARGET_ID_REGEX = re.compile(r'^[0-9A-Z\-]+$')

  def _VerifyEscrowPermission(self):
    try:
      base.GetCurrentUser()
    except base.AccessDeniedError:
      pass
    else:
      return super(HpFirmwarePassword, self)._VerifyEscrowPermission()
    raise base.AccessDeniedError

  def _CreateNewSecretEntity(self, owner, target_id, secret):
    return firmware.HpFirmwarePassword(
        owner=owner,
        serial=target_id,
        password=str(secret))


  def IsValidSecret(self, secret):
    return self.IsValidTargetId(secret)

  def Publish(self, _):
    pass
