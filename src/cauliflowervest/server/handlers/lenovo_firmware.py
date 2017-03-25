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
"""Module to handle interactions with Lenovo Firmware Passwords."""

import re

from cauliflowervest import settings as base_settings
from cauliflowervest.server import permissions
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.handlers import passphrase_handler
from cauliflowervest.server.models import base
from cauliflowervest.server.models import firmware


class LenovoFirmwarePassword(passphrase_handler.PassphraseHandler):
  """Handler for /lenovo_firmware URL."""
  AUDIT_LOG_MODEL = firmware.LenovoFirmwarePasswordAccessLog
  SECRET_MODEL = firmware.LenovoFirmwarePassword
  PERMISSION_TYPE = permissions.TYPE_LENOVO_FIRMWARE

  TARGET_ID_REGEX = re.compile(r'^[0-9A-Z\-]+$')
  SECRET_REGEX = re.compile(
      r'^[bcdefghjknprstuvxBCDEFGHJKNPRSTUVX23456789]{10}$')

  def _VerifyEscrowPermission(self):
    try:
      base.GetCurrentUser()
    except base.AccessDeniedError:
      pass
    else:
      return super(LenovoFirmwarePassword, self)._VerifyEscrowPermission()
    raise base.AccessDeniedError

  def _CreateNewSecretEntity(self, owner, target_id, secret):
    return firmware.LenovoFirmwarePassword(
        owner=owner,
        serial=target_id,
        password=str(secret))


  def IsValidSecret(self, secret):
    """Returns true if secret str is a well formatted."""
    return self.SECRET_REGEX.match(secret) is not None

  def Publish(self, _):
    pass
