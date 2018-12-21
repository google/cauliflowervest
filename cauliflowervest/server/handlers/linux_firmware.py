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

"""Module to handle interactions with Linux Firmware Passwords."""

from cauliflowervest.server import permissions
from cauliflowervest.server.handlers import change_owner_handler
from cauliflowervest.server.handlers import firmware_handler
from cauliflowervest.server.models import firmware as firmware_model


class LinuxFirmwarePassword(firmware_handler.FirmwarePasswordHandler):
  """Handler for /linux_firmware URL."""
  TARGET_ID_REGEX = None
  AUDIT_LOG_MODEL = firmware_model.LinuxFirmwarePasswordAccessLog
  SECRET_MODEL = firmware_model.LinuxFirmwarePassword
  PERMISSION_TYPE = permissions.TYPE_LINUX_FIRMWARE


class LinuxFirmwarePasswordChangeOwner(change_owner_handler.ChangeOwnerHandler):
  """Handle to allow changing the owner of an existing LinuxFirmwarePassword."""
  SECRET_MODEL = firmware_model.LinuxFirmwarePassword
  PERMISSION_TYPE = permissions.TYPE_LINUX_FIRMWARE
