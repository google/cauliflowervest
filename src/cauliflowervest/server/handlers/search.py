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




import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import settings


def VolumesForQuery(q):
  """Search for models.FileVaultVolume matching the string query."""
  query = models.FileVaultVolume.all()
  query.filter('active =', True)

  fields = q.split(' ')
  for field in fields:
    name, value = field.strip().split(':')
    if name == 'created_by':
      value = users.User('%s@%s' % (value, settings.AUTH_DOMAIN))
    query.filter(name + ' =', value)

  volumes = query.fetch(999)
  volumes.sort(key=lambda x: x.created, reverse=True)
  return volumes


class Search(handlers.FileVaultAccessHandler, webapp.RequestHandler):
  """Handler for /search URL."""

  def get(self):  # pylint: disable-msg=C6409
    """Handles GET requests."""
    unused_user = self.VerifyPermissions(permissions.SEARCH)
    value1 = self.request.get('value1').strip()
    field1 = self.request.get('field1')
    if field1 and value1:
      # TODO(user): implement mutli-field search by building query here or
      #   better yet using JavaScript.
      q = '%s:%s' % (field1, value1)
      template_name = 'search_result.html'
      params = {
          'q': q,
          'volumes': VolumesForQuery(q),
          }
    else:
      template_name = 'search_form.html'
      params = {'fields': models.FileVaultVolume.SEARCH_FIELDS}
    self.response.out.write(template.render(
        os.path.join(settings.TEMPLATE_DIR, template_name), params))