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

"""Retrieve firmware passwords for retired assets."""

from cauliflowervest.server import permissions
from cauliflowervest.server import service_factory
from cauliflowervest.server import util
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.models import base
from cauliflowervest.server.models import firmware


class RetiredAssets(base_handler.BaseHandler):
  """Handler for /api/internal/retired-assets URL."""

  def get(self, serials):
    base_handler.VerifyPermissions(
        permissions.RETRIEVE, base.GetCurrentUser(),
        permissions.TYPE_APPLE_FIRMWARE)

    inventory_service = service_factory.GetInventoryService()
    res = {
        'active': [],
        'retired': [],
    }
    for serial in serials.split(','):
      if not inventory_service.IsRetiredMac(serial):
        res['active'].append(serial)
        continue

      entity = firmware.AppleFirmwarePassword.GetLatestForTarget(serial)
      if entity:
        firmware.AppleFirmwarePasswordAccessLog.Log(
            message='GET', entity=entity, request=self.request)

        res['retired'].append({'serial': serial, 'password': entity.password})
      else:
        res['retired'].append({'serial': serial, 'password': 'N/A'})

    self.response.write(util.ToSafeJson(res))
