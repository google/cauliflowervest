#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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
"""Module to provide information about volume types to ui."""

import webapp2

from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import util


class VolumeTypes(webapp2.RequestHandler):
  """Handler exposes searchable fields to the search UI for each volume type."""

  def get(self):
    search_perms = handlers.VerifyAllPermissionTypes(permissions.SEARCH)
    params = {}
    if search_perms[permissions.TYPE_BITLOCKER]:
      params['bitlocker_fields'] = models.BitLockerVolume.SEARCH_FIELDS
    if search_perms[permissions.TYPE_FILEVAULT]:
      params['filevault_fields'] = models.FileVaultVolume.SEARCH_FIELDS
    if search_perms[permissions.TYPE_LUKS]:
      params['luks_fields'] = models.LuksVolume.SEARCH_FIELDS
    if search_perms[permissions.TYPE_PROVISIONING]:
      provisioning_fields = models.ProvisioningVolume.SEARCH_FIELDS
      params['provisioning_fields'] = provisioning_fields

    self.response.out.write(util.ToSafeJson(params))
