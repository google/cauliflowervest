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

"""Module to view AccessLog entities."""

from google.appengine.ext import db

from cauliflowervest.server import permissions
from cauliflowervest.server import util
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.models import base
from cauliflowervest.server.models import util as models_util

PER_PAGE = 25


class Logs(base_handler.BaseHandler):
  """Handler for /logs URL."""

  def get(self):
    """Handles GET requests."""
    log_type = self.request.get('log_type')
    base_handler.VerifyPermissions(
        permissions.MASTER, base.GetCurrentUser(), log_type)

    start = self.request.get('start_next', None)
    log_model = models_util.TypeNameToLogModel(log_type)
    logs_query = log_model.all()

    if self.request.get('only_errors', 'false') == 'true':
      logs_query.filter('successful =', False)

    logs_query.order('-paginate_mtime')
    if start:
      logs_query.filter('paginate_mtime <', start)

    logs = logs_query.fetch(PER_PAGE + 1)
    more = len(logs) == PER_PAGE + 1
    start_next = None
    if more:
      start_next = logs[-1].paginate_mtime

    logs = [db.to_dict(log) for log in logs[:PER_PAGE]]
    for log in logs:
      log['user'] = str(log['user'])
      log['mtime'] = str(log['mtime'])
    params = {
        'logs': logs,
        'log_type': log_type,
        'more': more,
        'start': start,
        'start_next': start_next,
    }

    self.response.out.write(util.ToSafeJson(params))
