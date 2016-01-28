#!/usr/bin/env python
#
# Copyright 2011 Google Inc. All Rights Reserved.
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

"""FileVaultClient."""




# Because of OSS
# pylint: disable=g-line-too-long

# Importing this module before appengine_rpc in OSS version is necessary
# because PyObjC does some ugliness with imports that isn't compatible
# with zip package imports.
# pylint: disable=g-bad-import-order
from cauliflowervest.client.mac import machine_data

from cauliflowervest import settings as base_settings
from cauliflowervest.client import base_client


class FileVaultClient(base_client.CauliflowerVestClient):
  """Client to perform FileVault operations."""

  ESCROW_PATH = '/filevault'
  REQUIRED_METADATA = base_settings.FILEVAULT_REQUIRED_PROPERTIES

  def _GetMetadata(self):
    """Returns a dict of key/value metadata pairs."""
    return machine_data.Get()
