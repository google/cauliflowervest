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

"""Main module for CauliflowerVest including wsgi URL mappings."""




import webapp2

from cauliflowervest.server import settings
from cauliflowervest.server.handlers import bitlocker
from cauliflowervest.server.handlers import created
from cauliflowervest.server.handlers import duplicity
from cauliflowervest.server.handlers import filevault
from cauliflowervest.server.handlers import logs
from cauliflowervest.server.handlers import luks
from cauliflowervest.server.handlers import provisioning
from cauliflowervest.server.handlers import search
from cauliflowervest.server.handlers import xsrf


class Home(webapp2.RequestHandler):
  """Redirects from "/" to the search page.

  Should be replaced if/when there is a better "home" page.
  """

  def get(self):  # pylint: disable=g-bad-name
    """Handle GET."""
    self.redirect('/search')


class Warmup(webapp2.RequestHandler):
  """Response with HTTP 200 for GAE warmup handling."""

  def get(self):  # pylint: disable=g-bad-name
    """Handle GET."""
    self.response.out.write('warmed up!')


app = webapp2.WSGIApplication([
    (r'/?$', Home),
    (r'/_ah/warmup$', Warmup),
    (r'/bitlocker/([\w\d\-]+)/?$', bitlocker.BitLocker),
    (r'/duplicity/([\w\d\-]+)/?$', duplicity.Duplicity),
    (r'/filevault/([\w\d\-]+)/?$', filevault.FileVault),
    (r'/filevault/([\w\d\-]+)/change-owner/?$', filevault.FileVaultChangeOwner),
    (r'/logs$', logs.Logs),
    (r'/luks/([\w\d_\.-]+)/?$', luks.Luks),
    (r'/search$', search.Search),
    (r'/created$', created.Created),
    (r'/provisioning/([\w\d\-]+)/?$', provisioning.Provisioning),
    (r'/xsrf-token/([\w]+)/?$', xsrf.Token),
    ], debug=settings.DEBUG)
