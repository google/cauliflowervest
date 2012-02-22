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
#

"""URL mappings for CauliflowerVest."""




from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from cauliflowervest.server.handlers import filevault
from cauliflowervest.server.handlers import logs
from cauliflowervest.server.handlers import search


class Home(webapp.RequestHandler):
  """Redirects from "/" to the search page.

  Should be replaced if/when there is a better "home" page.
  """

  def get(self):  # pylint: disable-msg=C6409
    """Handle GET."""
    self.redirect('/search')


class Warmup(webapp.RequestHandler):
  """Response with HTTP 200 for GAE warmup handling."""

  def get(self):  # pylint: disable-msg=C6409
    """Handle GET."""
    self.response.out.write('warmed up!')


application = webapp.WSGIApplication([
    (r'/filevault/([\w\d\-]+)/?$', filevault.FileVault),
    (r'/logs$', logs.Logs),
    (r'/search$', search.Search),
    (r'/_ah/warmup$', Warmup),
    (r'/?$', Home),
    ], debug=True)


def main():
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()