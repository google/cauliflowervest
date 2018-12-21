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

"""Module to handle interactions with Apple Firmware Passwords."""

from cauliflowervest.server import permissions
from cauliflowervest.server.handlers import change_owner_handler
from cauliflowervest.server.handlers import firmware_handler
from cauliflowervest.server.models import firmware as firmware_model


class AppleFirmwarePassword(firmware_handler.FirmwarePasswordHandler):
  """Handler for /apple_firmware URL."""
  AUDIT_LOG_MODEL = firmware_model.AppleFirmwarePasswordAccessLog
  SECRET_MODEL = firmware_model.AppleFirmwarePassword
  PERMISSION_TYPE = permissions.TYPE_APPLE_FIRMWARE


class AppleFirmwarePasswordChangeOwner(change_owner_handler.ChangeOwnerHandler):
  """Handle to allow changing the owner of an existing AppleFirmwarePassword."""
  SECRET_MODEL = firmware_model.AppleFirmwarePassword
  PERMISSION_TYPE = permissions.TYPE_APPLE_FIRMWARE
