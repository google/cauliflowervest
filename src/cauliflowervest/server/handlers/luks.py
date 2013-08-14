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
# #

"""Module to handle interaction with a Luks key."""

from cauliflowervest import settings as base_settings
from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions


class Luks(handlers.LuksAccessHandler):
  """Handler for /luks URL."""

  def VerifyEscrow(self, volume_uuid):
    """Handles a GET to verify if a volume uuid has an escrowed passphrase."""
    # NOTE(user): In production, we have seen UUIDs with a trailing /
    volume_uuid = volume_uuid.rstrip('/')

    return super(Luks, self).VerifyEscrow(volume_uuid)

  # pylint: disable=g-bad-name
  def put(self, volume_uuid=None):
    """Handles PUT requests."""
    self.VerifyPermissions(permissions.ESCROW)
    self.VerifyXsrfToken(base_settings.SET_PASSPHRASE_ACTION)

    recovery_token = self.GetSecretFromBody()
    if volume_uuid and recovery_token:
      self.PutNewPassphrase(volume_uuid, recovery_token, self.request)
    else:
      self.AUDIT_LOG_MODEL.Log(message='Unknown PUT', request=self.request)
      self.error(400)

  def PutNewPassphrase(self, volume_uuid, passphrase, metadata):
    """Puts a new LuksVolume entity to Datastore.

    Args:
      volume_uuid: str, Volume UUID associated to the passphrase to put.
      passphrase: str, FileVault2 passphrase / recovery token.
      metadata: dict, dict of str metadata with keys matching
          models.LuksVolume property names.
    """
    if not volume_uuid:
      raise models.LuksAccessError('volume_uuid is required', self.request)

    entity = models.LuksVolume(
        key_name=volume_uuid,
        volume_uuid=volume_uuid,
        passphrase=str(passphrase))

    for prop_name in entity.properties():
      value = metadata.get(prop_name)
      if value:
        setattr(entity, prop_name, self.SanitizeString(value))

    entity.put()

    self.AUDIT_LOG_MODEL.Log(entity=entity, message='PUT', request=self.request)

    self.response.out.write('Passphrase successfully escrowed!')