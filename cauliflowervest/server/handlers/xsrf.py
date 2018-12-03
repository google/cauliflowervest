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

"""Module to generate XSRF tokens."""

import httplib

from cauliflowervest.server import util
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.models import base
from cauliflowervest.server.models import errors


class Token(base_handler.BaseHandler):
  """Handler for /xsrf-token/ URL."""

  def get(self, action=None):
    """Handles GET requests."""
    if not action:
      self.error(httplib.NOT_FOUND)
      return

    try:
      email = base.GetCurrentUser().email
    except errors.AccessDeniedError:
      raise errors.AccessDeniedError
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write(util.XsrfTokenGenerate(action, user=email))
