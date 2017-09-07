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
#
"""Duplicity keypair client."""



# Because of OSS
# pylint: disable=g-line-too-long

from cauliflowervest import settings as base_settings
from cauliflowervest.client import base_client


class DuplicityClient(base_client.CauliflowerVestClient):
  """Client to perform Duplicity operations."""

  ESCROW_PATH = '/duplicity/'
  PASSPHRASE_KEY = 'key_pair'
  REQUIRED_METADATA = base_settings.DUPLICITY_REQUIRED_PROPERTIES

  # Alias the RetrieveSecret method for naming consistency.
  # pylint: disable=g-bad-name
  RetrieveKeyPair = base_client.CauliflowerVestClient.RetrieveSecret

  def UploadKeyPair(self, volume_uuid, key_pair, metadata):
    self._metadata = metadata
    super(DuplicityClient, self).UploadPassphrase(volume_uuid, key_pair)
