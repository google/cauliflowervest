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

"""Syncs metadata changes from Inventory Service."""
import logging
import uuid
import webapp2

from google.appengine.ext import deferred

from cauliflowervest.server import service_factory
from cauliflowervest.server import util
from cauliflowervest.server.models import firmware
from cauliflowervest.server.models import volumes


_QUEUE_NAME = 'cron'
_DELAY = 1
_BATCH_SIZE = 500


def _deferred_name(model):
  return 'inventory_sync_%s_%s' % (
      model.ESCROW_TYPE_NAME, uuid.uuid4())


def _sync_metadata(model, cursor=None, total_updated=0):
  """Sync metadata from Inventory Service."""
  query = model.all().filter('active =', True)
  if cursor:
    query.with_cursor(cursor)
  entities = query.fetch(limit=_BATCH_SIZE)
  if not entities:
    logging.info('Total updated %s %d', model.ESCROW_TYPE_NAME, total_updated)
    return

  inventory_service = service_factory.GetInventoryService()
  for e in entities:
    changes = inventory_service.GetMetadataUpdates(e)

    updated = False
    if 'owners' in changes:
      if e.ChangeOwners(changes['owners']):
        updated = True

    if 'hostname' in changes and changes['hostname'] != e.hostname:
      logging.info('targetid %s old hostname %s -> %s',
                   e.target_id, e.hostname, changes['hostname'])
      e.UpdateMutableProperty('hostname', changes['hostname'])
      updated = True

    if updated:
      total_updated += 1

  if entities:
    deferred.defer(
        _sync_metadata, model, cursor=query.cursor(), _countdown=_DELAY,
        _name=_deferred_name(model), total_updated=total_updated,
        _queue=_QUEUE_NAME)


class InventorySync(webapp2.RequestHandler):
  """Sync metadata from Inventory Service."""

  @util.CronJob
  def get(self):
    sync_activated = [firmware.AppleFirmwarePassword,
                      firmware.LinuxFirmwarePassword,
                      volumes.BitLockerVolume]

    for model in sync_activated:
      deferred.defer(
          _sync_metadata, model, _queue=_QUEUE_NAME, _countdown=_DELAY,
          _name=_deferred_name(model))
