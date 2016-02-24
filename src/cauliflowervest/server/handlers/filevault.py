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

"""Module to handle interaction with a FileVault."""



import re

from cauliflowervest import settings as base_settings
from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions


class FileVault(handlers.FileVaultAccessHandler):
  """Handler for /filevault URL."""

  UUID_REGEX = re.compile(r'^[0-9A-Z\-]+$')

  def _CreateNewSecretEntity(self, owner, volume_uuid, secret):
    return models.FileVaultVolume(
        owner=owner,
        volume_uuid=volume_uuid,
        passphrase=str(secret))

  def IsValidSecret(self, secret):
    return self.IsValidUuid(secret)


# TODO(user): accept created as argument
class FileVaultChangeOwner(handlers.FileVaultAccessHandler):
  """Handle to allow changing the owner of an existing FileVaultVolume."""

  def dispatch(self):  # pylint: disable=g-bad-name
    volume_uuid = self.request.route_args[0]
    self.entity = models.FileVaultVolume.GetLatestByUuid(volume_uuid)
    if self.entity:
      return super(FileVaultChangeOwner, self).dispatch()
    else:
      self.error(404)

  def post(self, volume_uuid):  # pylint: disable=g-bad-name
    """Handles POST requests."""
    self.VerifyXsrfToken(base_settings.CHANGE_OWNER_ACTION)
    self.VerifyPermissions(permissions.CHANGE_OWNER)
    new_entity = self.entity.Clone()
    new_entity.owner = self.request.get('new_owner')
    new_entity.put()
    self.AUDIT_LOG_MODEL.Log(
        entity=self.entity, request=self.request, message=(
            'Owner changed from "%s" to "%s"' %
            (self.entity.owner, new_entity.owner)))
