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
"""Module to handle display of created passphrases."""




import datetime

from google.appengine.api import users
from google.appengine.ext import db

from cauliflowervest import settings as base_settings
from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import util

PROVISIONING_FILTER_SECONDS = 60 * 60 * 24


def ProvisioningVolumesForUser(user, time_s):
  """Find provisioning volumes, created by the user in the last n seconds.

  Args:
    user: users.user object of the user that created the secrets.
    time_s: integer, amount of seconds of time passed for query to filter
      through.
  Returns:
    list of entities created by user in the last n seconds.
  Raises:
    ValueError: the given search_type is unknown.
  """

  model = models.ProvisioningVolume
  query = model.all()

  time = datetime.datetime.now() - datetime.timedelta(seconds=time_s)
  query.filter('created_by' ' =', user).filter('created' ' >', time)
  volumes = query.fetch(999)
  volumes.sort(key=lambda x: x.created, reverse=True)
  return volumes


class Created(handlers.AccessHandler):
  """Handler for /created URL."""

  def get(self):  # pylint: disable=g-bad-name
    """Handles GET requests."""

    # Get the user's search and retrieve permissions for all permission types.
    search_perms = self.VerifyAllPermissionTypes(permissions.SEARCH)
    retrieve_perms = self.VerifyAllPermissionTypes(permissions.RETRIEVE_OWN)
    retrieve_created = self.VerifyAllPermissionTypes(
        permissions.RETRIEVE_CREATED_BY)

    # Ensure user has provisioning search permissions.
    search_type = 'provisioning'
    if (not search_perms.get(search_type)
        and not retrieve_perms.get(search_type)
        and not retrieve_created.get(search_type)):
      raise models.AccessDeniedError('User lacks %s permission' % search_type)

    user = models.GetCurrentUser()
    user_nickname = user.user.nickname()
    provisioning_user = users.get_current_user()

    if search_perms[permissions.TYPE_PROVISIONING]:
      provisioning_fields = models.ProvisioningVolume.SEARCH_FIELDS
      try:
        volumes = ProvisioningVolumesForUser(provisioning_user,
                                             PROVISIONING_FILTER_SECONDS)
        volumes = [db.to_dict(volume) for volume in volumes]
        for volume in volumes:
          volume['created_by'] = str(volume['created_by'])
          volume['created'] = str(volume['created'])
      except ValueError:
        self.error(404)
        return

      template_name = 'created_list.html'
      params = {'provisioning_fields': provisioning_fields,
                'user_nickname': user_nickname,
                'search_type': search_type,
                'volumes': volumes}

      params['xsrf_token'] = util.XsrfTokenGenerate(
          base_settings.GET_PASSPHRASE_ACTION)

    if self.request.get('json', False):
      self.response.out.write(util.ToSafeJson(params))
    else:
      self.RenderTemplate(template_name, params)
