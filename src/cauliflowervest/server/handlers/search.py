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
# #

"""Module to handle searching for escrowed passphrases."""




import logging
import os
import re
from google.appengine.api import users

from cauliflowervest import settings as base_settings
from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import util


def VolumesForQuery(q, model, prefix_search):
  """Search a model for matching the string query."""
  query = model.all()

  fields = q.split(' ')
  for field in fields:
    try:
      name, value = field.strip().split(':')
    except ValueError:
      logging.info('Invalid field (%r) in query: %r', field, q)
      continue

    if name == 'created_by':
      if '@' not in value:
        value = '%s@%s' % (value, os.environ.get('AUTH_DOMAIN'))
      value = users.User(value)
    elif name == 'hostname':
      value = value.upper()
    if prefix_search and name != 'created_by':
      query.filter('%s >=' % name, value).filter(
          '%s <' % name, value + u'\ufffd')
    else:
      query.filter(name + ' =', value)

  volumes = query.fetch(999)
  volumes.sort(key=lambda x: x.created, reverse=True)
  return volumes


class Search(handlers.AccessHandler):
  """Handler for /search URL."""
  # TODO(user): Use XHR(AJAX) to display barcode directly inline.

  SEARCH_TYPES = ('bitlocker', 'filevault', 'luks')

  def get(self):  # pylint: disable=g-bad-name
    """Handles GET requests."""
    # Get the user's search permissions for all permission types.
    perms = self.VerifyAllPermissionTypes(permissions.SEARCH)

    # If the user is performing a search, ensure they have permissions.
    search_type = self.request.get('search_type')
    if search_type and not perms.get(search_type):
      raise models.AccessDeniedError(
          'User lacks %s permission' % search_type, self.request)

    template_name = None
    queried = False
    params = {}

    if search_type in self.SEARCH_TYPES:
      field1 = self.request.get('field1')
      value1 = self.request.get('value1').strip()
      if field1 and value1:
        queried = True
        prefix_search = self.request.get('prefix_search', '0') == '1'
        # TODO(user): implement multi-field search by building query here
        #   or better yet using JavaScript.
        q = '%s:%s' % (field1, value1)
        if search_type == 'bitlocker':
          volumes = VolumesForQuery(q, models.BitLockerVolume, prefix_search)
        elif search_type == 'filevault':
          volumes = VolumesForQuery(q, models.FileVaultVolume, prefix_search)
        elif search_type == 'luks':
          volumes = VolumesForQuery(q, models.LuksVolume, prefix_search)
        else:
          self.error(404)
        template_name = 'search_result.html'
        params = {'q': q, 'search_type': search_type, 'volumes': volumes}

    if not queried:
      template_name = 'search_form.html'
      params = {}
      if perms[permissions.TYPE_BITLOCKER]:
        params['bitlocker_fields'] = models.BitLockerVolume.SEARCH_FIELDS
      if perms[permissions.TYPE_FILEVAULT]:
        params['filevault_fields'] = models.FileVaultVolume.SEARCH_FIELDS
      if perms[permissions.TYPE_LUKS]:
        params['luks_fields'] = models.LuksVolume.SEARCH_FIELDS

    params['xsrf_token'] = util.XsrfTokenGenerate(
        base_settings.GET_PASSPHRASE_ACTION)
    self.RenderTemplate(template_name, params)