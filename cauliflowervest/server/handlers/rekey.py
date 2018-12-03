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

"""Provide passphrase status to client."""

import logging

from google.appengine.api import memcache

from cauliflowervest.server import util
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.models import base
from cauliflowervest.server.models import util as models_util


class IsRekeyNeeded(base_handler.BaseHandler):
  """Check if rekeying needed."""

  def get(self, type_name, target_id):
    """Handles GET requests."""
    user = base.GetCurrentUser()
    tag = self.request.get('tag', 'default')

    entity = models_util.TypeNameToModel(
        type_name).GetLatestForTarget(target_id, tag)
    if not entity:
      if memcache.Client().get(target_id, namespace='experimental_rekey'):
        logging.info('experimental_rekey %s', target_id)
        self.response.write(util.ToSafeJson('experimental'))
        return
      self.response.write(util.ToSafeJson(False))
      return

    if user.email not in entity.owners:
      logging.warning(
          'owner mismatch %s %s', entity.owners, user.email)
      # Passphrase retrieval is necessary for rekeying so we abort.
      self.response.write(util.ToSafeJson(False))
      return

    self.response.write(util.ToSafeJson(bool(entity.force_rekeying)))
