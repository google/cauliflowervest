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

"""Base class for handler to change the owner of an existing passphrase."""

import httplib
import logging

from google.appengine.ext import db

from cauliflowervest import settings as base_settings
from cauliflowervest.server import permissions
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.models import base


class ChangeOwnerHandler(base_handler.BaseHandler):
  """Base class handler to change the owner of an existing passphrase."""

  # Below constants must be defined in children classes.
  AUDIT_LOG_MODEL = None
  SECRET_MODEL = None
  PERMISSION_TYPE = None

  def post(self, volume_key):
    """Handles POST requests."""
    try:
      db_key = db.Key(volume_key)
    except db.BadKeyError as e:
      logging.warning('Bad volume_key "%s" provided: %s', volume_key, e)
      return self.error(httplib.NOT_FOUND)

    self.entity = self.SECRET_MODEL.get(db_key)
    if not self.entity:
      return self.error(httplib.NOT_FOUND)
    if self.entity and not self.entity.active:
      return self.error(httplib.BAD_REQUEST)

    self.VerifyXsrfToken(base_settings.CHANGE_OWNER_ACTION)
    base_handler.VerifyPermissions(
        permissions.CHANGE_OWNER, base.GetCurrentUser(), self.PERMISSION_TYPE)

    new_entity = self.entity.Clone()
    new_entity.owners = [self.request.get('new_owner')]
    new_entity.put()

    self.AUDIT_LOG_MODEL.Log(
        entity=self.entity,
        request=self.request,
        message=('Owner changed from "%s" to "%s"' % (self.entity.owner,
                                                      new_entity.owner)))
