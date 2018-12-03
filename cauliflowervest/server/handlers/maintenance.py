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

"""Module to help with updating schema."""

import httplib
import logging

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import deferred

from cauliflowervest import settings as base_settings
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.models import base
from cauliflowervest.server.models import util


_BATCH_SIZE = 20
_QUEUE_NAME = 'serial'


@db.transactional()
def _reinsert_entity(model, entity_key):
  entity = model.get(entity_key)
  entity.tag = getattr(entity, 'tag', 'default')
  super(base.BasePassphrase, entity).put()


def _update_schema(model, cursor=None, num_updated=0):
  """Add tag field."""
  query = model.all()
  if cursor:
    query.with_cursor(cursor)

  updated = 0
  for p in query.fetch(limit=_BATCH_SIZE):
    _reinsert_entity(model, p.key())
    updated += 1

  if updated > 0:
    num_updated += updated
    logging.info(
        'Put %d %s entities to Datastore for a total of %d',
        updated, model.ESCROW_TYPE_NAME, num_updated)
    deferred.defer(
        _update_schema, model, cursor=query.cursor(),
        num_updated=num_updated, _queue=_QUEUE_NAME, _countdown=20)
  else:
    logging.info(
        'UpdateSchema complete for %s with %d updates!', model.ESCROW_TYPE_NAME,
        num_updated)


class UpdateVolumesSchema(base_handler.BaseHandler):
  """Puts all Volumes entities so any new properties are created."""

  def get(self, action=None):
    """Handles GET requests."""
    self.VerifyXsrfToken(base_settings.MAINTENANCE_ACTION)

    if not users.is_current_user_admin():
      self.error(httplib.FORBIDDEN)
      return

    for model in util.AllModels():
      deferred.defer(
          _update_schema, model, _queue=_QUEUE_NAME, _countdown=5)

    self.response.out.write('Schema migration successfully initiated.')
