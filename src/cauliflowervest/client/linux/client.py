#!/usr/bin/env python
#
# Copyright 2015 Google Inc. All Rights Reserved.
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
#"""Client enables escrow of LUKS keys and temporary passwords."""




# Because of OSS
# pylint: disable=g-line-too-long

from cauliflowervest import settings as base_settings
from cauliflowervest.client import base_client


class LuksClient(base_client.CauliflowerVestClient):
  """Client to perform Luks operations."""

  ESCROW_PATH = '/luks'
  REQUIRED_METADATA = base_settings.LUKS_REQUIRED_PROPERTIES

  def UploadPassphrase(self, volume_uuid, passphrase, metadata):
    self._metadata = metadata
    super(LuksClient, self).UploadPassphrase(volume_uuid, passphrase)


class ProvisioningClient(base_client.CauliflowerVestClient):
  """CauliflowerVest client for the provisioning escrow domain."""

  ESCROW_PATH = '/provisioning'
  REQUIRED_METADATA = base_settings.PROVISIONING_REQUIRED_PROPERTIES

  def UploadPassphrase(self, volume_uuid, passphrase, metadata):
    self._metadata = metadata
    super(ProvisioningClient, self).UploadPassphrase(volume_uuid, passphrase)
