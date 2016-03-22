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
"""Module to help with updating schema."""

import httplib
import logging


import webapp2

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import deferred

from cauliflowervest import settings as base_settings
from cauliflowervest.server import models
from cauliflowervest.server import settings
from cauliflowervest.server import util


BATCH_SIZE = 100


def _UpdateSchema(model, cursor=None, num_updated=0):
  """Add tag field."""
  query = model.all()
  if cursor:
    query.with_cursor(cursor)

  to_put = []
  for p in query.fetch(limit=BATCH_SIZE):
    p.tag = getattr(p, 'tag', 'default')
    to_put.append(p)

  if to_put:
    # does not call BaseVolume.put
    db.put(to_put)

    num_updated += len(to_put)
    logging.debug(
        'Put %d %s entities to Datastore for a total of %d',
        len(to_put), model.ESCROW_TYPE_NAME, num_updated)
    deferred.defer(
        _UpdateSchema, model, cursor=query.cursor(),
        num_updated=num_updated)
  else:
    logging.debug(
        'UpdateSchema complete for %s with %d updates!', model.ESCROW_TYPE_NAME,
        num_updated)


class UpdateVolumesSchema(webapp2.RequestHandler):
  """Puts all Volumes entities so any new properties are created."""

  # pylint: disable=g-bad-name
  def get(self, action=None):
    """Handles GET requests."""
    if settings.XSRF_PROTECTION_ENABLED:
      xsrf_token = self.request.get('xsrf-token', None)
      if not util.XsrfTokenValidate(
          xsrf_token, base_settings.MAINTENANCE_ACTION):
        self.error(httplib.FORBIDDEN)
        return

    if not users.is_current_user_admin():
      self.error(httplib.FORBIDDEN)
      return
    deferred.defer(_UpdateSchema, models.LuksVolume)
    deferred.defer(_UpdateSchema, models.FileVaultVolume)
    deferred.defer(_UpdateSchema, models.BitLockerVolume)
    deferred.defer(_UpdateSchema, models.DuplicityKeyPair)
    self.response.out.write('Schema migration successfully initiated.')
