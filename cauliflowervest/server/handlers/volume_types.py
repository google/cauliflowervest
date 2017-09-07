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
"""Module to provide information about volume types to ui."""
import collections
import webapp2

from cauliflowervest.server import permissions
from cauliflowervest.server import util
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.models import base
from cauliflowervest.server.models import util as model_util


class VolumeTypes(webapp2.RequestHandler):
  """Handler exposes searchable fields to the search UI for each volume type."""

  def get(self):
    params = collections.defaultdict(dict)

    search_perms = base_handler.VerifyAllPermissionTypes(permissions.SEARCH)

    for model_type in search_perms:
      if not search_perms[model_type]:
        continue
      model = model_util.TypeNameToModel(model_type)
      if not hasattr(model, 'SEARCH_FIELDS'):
        continue
      params[model_type]['fields'] = model.SEARCH_FIELDS

    can_retrieve_own = False
    retrieve_own_perms = base_handler.VerifyAllPermissionTypes(
        permissions.RETRIEVE_OWN)
    for volume_type in retrieve_own_perms:
      if retrieve_own_perms[volume_type]:
        params[volume_type][permissions.RETRIEVE_OWN] = True
        can_retrieve_own = True

    if can_retrieve_own:
      params['user'] = base.GetCurrentUser().user.nickname()

    self.response.out.write(util.ToSafeJson(params))
