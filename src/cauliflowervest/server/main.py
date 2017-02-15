#!/usr/bin/env python
#
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
#
"""Main module for CauliflowerVest including wsgi URL mappings."""

import webapp2

from cauliflowervest.server import settings
from cauliflowervest.server.handlers import apple_firmware
from cauliflowervest.server.handlers import bitlocker
from cauliflowervest.server.handlers import created
from cauliflowervest.server.handlers import duplicity
from cauliflowervest.server.handlers import filevault
from cauliflowervest.server.handlers import lenovo_firmware
from cauliflowervest.server.handlers import logs
from cauliflowervest.server.handlers import luks
from cauliflowervest.server.handlers import maintenance
from cauliflowervest.server.handlers import provisioning
from cauliflowervest.server.handlers import rekey
from cauliflowervest.server.handlers import search
from cauliflowervest.server.handlers import volume_types
from cauliflowervest.server.handlers import xsrf
from cauliflowervest.server.models import base


class Home(webapp2.RequestHandler):
  """Redirects from "/" to the search page."""

  def get(self):  # pylint: disable=g-bad-name
    """Handle GET."""
    self.redirect('/ui/')


class Warmup(webapp2.RequestHandler):
  """Response with HTTP 200 for GAE warmup handling."""

  def get(self):  # pylint: disable=g-bad-name
    """Handle GET."""
    self.response.out.write('warmed up!')


app = webapp2.WSGIApplication([
    (r'/?$', Home),
    (r'/ui$', Home),
    (r'/_ah/warmup$', Warmup),
    (
        r'/bitlocker/([\w\d\-]*)/?$',
        bitlocker.BitLocker,
        base.VOLUME_ACCESS_HANDLER
    ),
    (
        r'/duplicity/([\w\d\-]*)/?$',
        duplicity.Duplicity,
        base.VOLUME_ACCESS_HANDLER
    ),
    (
        r'/filevault/([\w\d\-]*)/?$',
        filevault.FileVault,
        base.VOLUME_ACCESS_HANDLER
    ),
    (
        r'/apple_firmware/([\w\d\-]*)/?$',
        apple_firmware.AppleFirmwarePassword,
        base.VOLUME_ACCESS_HANDLER,
    ),
    (
        r'/lenovo_firmware/([\w\d\-]*)/?$',
        lenovo_firmware.LenovoFirmwarePassword,
        base.VOLUME_ACCESS_HANDLER,
    ),
    (r'/logs$', logs.Logs),
    (r'/luks/([\w\d_\.-]*)/?$', luks.Luks, base.VOLUME_ACCESS_HANDLER),
    (r'/search$', search.Search),
    (r'/created$', created.Created),
    (
        r'/provisioning/([\w\d\-]*)/?$',
        provisioning.Provisioning,
        base.VOLUME_ACCESS_HANDLER,
    ),
    (
        r'/xsrf-token/([\w]+)/?$',
        xsrf.Token,
        base.XSRF_TOKEN_GENERATE_HANDLER
    ),
    (r'/api/internal/volume_types$', volume_types.VolumeTypes),
    (
        r'/api/internal/change-owner/filevault/([\w\d\-]+)/?$',
        filevault.FileVaultChangeOwner,
    ),
    (
        r'/api/internal/maintenance/update_volumes_schema$',
        maintenance.UpdateVolumesSchema,
    ),
], debug=settings.DEBUG)
