#!/usr/bin/env python
#
# Copyright 2012 Google Inc. All Rights Reserved.
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
"""Module to generate XSRF tokens."""



import webapp2

from cauliflowervest.server import models
from cauliflowervest.server import util


class Token(webapp2.RequestHandler):
  """Handler for /xsrf-token/ URL."""

  # pylint: disable=g-bad-name
  def get(self, action=None):
    """Handles GET requests."""
    if not action:
      self.error(404)
      return

    try:
      models.GetCurrentUser()
    except models.AccessDeniedError:
      self.error(401)
      return

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write(util.XsrfTokenGenerate(action))
