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

"""LinuxFirmware client."""



from cauliflowervest import settings as base_settings
from cauliflowervest.client import base_client


class LinuxFirmwareClient(base_client.CauliflowerVestClient):
  """Client to perform LinuxFirmware operations."""

  ESCROW_PATH = '/linux_firmware/'
  REQUIRED_METADATA = base_settings.LINUX_FIRMWARE_REQUIRED_PROPERTIES


  def UploadPassphrase(self, target_id, passphrase, metadata):
    self._metadata = metadata
    super(LinuxFirmwareClient, self).UploadPassphrase(target_id, passphrase)
