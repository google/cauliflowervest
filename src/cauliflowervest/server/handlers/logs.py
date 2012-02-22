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

"""Module to handle viewing FileVaultAccessLog entities."""




import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import settings


PER_PAGE = 25


class Logs(handlers.FileVaultAccessHandler, webapp.RequestHandler):
  """Handler for /logs URL."""

  def get(self):  # pylint: disable-msg=C6409
    """Handles GET requests."""
    self.VerifyPermissions(permissions.MASTER)

    start = self.request.get('start_next', None)
    logs_query = models.FileVaultAccessLog.all()
    logs_query.order('-paginate_mtime')
    if start:
      logs_query.filter('paginate_mtime <', start)

    logs = logs_query.fetch(PER_PAGE + 1)
    more = len(logs) == PER_PAGE + 1
    start_next = None
    if more:
      start_next = logs[-1].paginate_mtime

    params = {
        'logs': logs[:PER_PAGE],
        'more': more,
        'start': start,
        'start_next': start_next,
        }
    self.response.out.write(template.render(
        os.path.join(settings.TEMPLATE_DIR, 'logs.html'), params))