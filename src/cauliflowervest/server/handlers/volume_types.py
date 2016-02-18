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
import collections


import webapp2

from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import util


class VolumeTypes(webapp2.RequestHandler):
  """Handler exposes searchable fields to the search UI for each volume type."""

  def get(self):
    params = collections.defaultdict(dict)

    search_perms = handlers.VerifyAllPermissionTypes(permissions.SEARCH)
    if search_perms[permissions.TYPE_BITLOCKER]:
      params['bitlocker']['fields'] = models.BitLockerVolume.SEARCH_FIELDS
    if search_perms[permissions.TYPE_FILEVAULT]:
      params['filevault']['fields'] = models.FileVaultVolume.SEARCH_FIELDS
    if search_perms[permissions.TYPE_LUKS]:
      params['luks']['fields'] = models.LuksVolume.SEARCH_FIELDS
    if search_perms[permissions.TYPE_PROVISIONING]:
      provisioning_fields = models.ProvisioningVolume.SEARCH_FIELDS
      params['provisioning']['fields'] = provisioning_fields

    can_retrieve_own = False
    retrieve_own_perms = handlers.VerifyAllPermissionTypes(
        permissions.RETRIEVE_OWN)
    for volume_type in retrieve_own_perms:
      if retrieve_own_perms[volume_type]:
        params[volume_type][permissions.RETRIEVE_OWN] = True
        can_retrieve_own = True

    if can_retrieve_own:
      params['user'] = models.GetCurrentUser().user.nickname()

    self.response.out.write(util.ToSafeJson(params))
