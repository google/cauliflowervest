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
#

"""Module to view AccessLog entities."""



from google.appengine.ext import db

from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import util

PER_PAGE = 25


class Logs(handlers.AccessHandler):
  """Handler for /logs URL."""

  def get(self):  # pylint: disable=g-bad-name
    """Handles GET requests."""
    log_type = self.request.get('log_type')
    self.VerifyPermissions(permissions.MASTER, permission_type=log_type)

    start = self.request.get('start_next', None)
    if log_type == 'bitlocker':
      log_model = models.BitLockerAccessLog
    elif log_type == 'duplicity':
      log_model = models.DuplicityAccessLog
    elif log_type == 'filevault':
      log_model = models.FileVaultAccessLog
    elif log_type == 'luks':
      log_model = models.LuksAccessLog
    elif log_type == 'provisioning':
      log_model = models.ProvisioningAccessLog
    else:
      raise ValueError('Unknown log_type')
    logs_query = log_model.all()
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
