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
"""Module to handle interaction with a FileVault."""

import httplib
import re

from google.appengine.ext import db

from cauliflowervest import settings as base_settings
from cauliflowervest.server import permissions
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.handlers import passphrase_handler
from cauliflowervest.server.models import base
from cauliflowervest.server.models import volumes as models


class FileVault(passphrase_handler.PassphraseHandler):
  """Handler for /filevault URL."""
  AUDIT_LOG_MODEL = models.FileVaultAccessLog
  SECRET_MODEL = models.FileVaultVolume
  PERMISSION_TYPE = permissions.TYPE_FILEVAULT

  TARGET_ID_REGEX = re.compile(r'^[0-9A-Z\-]+$')

  def _CreateNewSecretEntity(self, owner, volume_uuid, secret):
    return models.FileVaultVolume(
        owner=owner,
        volume_uuid=volume_uuid,
        passphrase=str(secret))

  def IsValidSecret(self, secret):
    return self.IsValidTargetId(secret)


class FileVaultChangeOwner(base_handler.BaseHandler):
  """Handle to allow changing the owner of an existing FileVaultVolume."""
  AUDIT_LOG_MODEL = models.FileVaultAccessLog
  SECRET_MODEL = models.FileVaultVolume
  PERMISSION_TYPE = permissions.TYPE_FILEVAULT

  def dispatch(self):
    volume_key = self.request.route_args[0]
    self.entity = models.FileVaultVolume.get(db.Key(volume_key))
    if self.entity:
      if self.entity.active:
        return super(FileVaultChangeOwner, self).dispatch()
      self.error(httplib.BAD_REQUEST)
    else:
      self.error(httplib.NOT_FOUND)

  def post(self, volume_key):
    """Handles POST requests."""
    self.VerifyXsrfToken(base_settings.CHANGE_OWNER_ACTION)
    base_handler.VerifyPermissions(
        permissions.CHANGE_OWNER, base.GetCurrentUser(),
        permissions.TYPE_FILEVAULT)
    new_entity = self.entity.Clone()
    new_entity.owner = self.request.get('new_owner')
    new_entity.put()
    self.AUDIT_LOG_MODEL.Log(
        entity=self.entity, request=self.request, message=(
            'Owner changed from "%s" to "%s"' %
            (self.entity.owner, new_entity.owner)))
