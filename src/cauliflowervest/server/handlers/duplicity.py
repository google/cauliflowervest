#!/usr/bin/env python
# 
# Copyright 2013 Google Inc. All Rights Reserved.
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

"""Module for handling Duplicity GPG key pairs."""



import re

from cauliflowervest import settings as base_settings
from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions


class Duplicity(handlers.DuplicityAccessHandler):
  """Handler for /duplicity URL."""

  JSON_SECRET_NAME = 'key_pair'
  UUID_REGEX = re.compile(r'^[a-f0-9]{32}$')

  def RetrieveSecret(self, volume_uuid):
    """Handles a GET request to retrieve a key pair."""
    self.request.json = '1'
    return super(Duplicity, self).RetrieveSecret(volume_uuid)

  def VerifyEscrow(self, volume_uuid):
    """Handles a GET to verify if a volume_uuid has an escrowed key pair."""
    self.VerifyPermissions(permissions.ESCROW)
    entity = models.DuplicityKeyPair.get_by_key_name(volume_uuid)
    if not entity:
      self.error(404)
    else:
      self.response.out.write('Escrow verified.')

  def get(self, volume_uuid=None):  # pylint: disable=g-bad-name
    """Handles GET requests."""
    if not volume_uuid:
      raise models.DuplicityAccessError('volume_uuid is required', self.request)

    if not self.IsSaneUuid(volume_uuid):
      raise models.DuplicityAccessError(
          'volume_uuid is malformed: %r' % volume_uuid, self.request)

    if self.request.get('only_verify_escrow'):
      self.VerifyEscrow(volume_uuid)
    else:
      self.RetrieveSecret(volume_uuid)

  def put(self, volume_uuid=None):  # pylint: disable=g-bad-name
    """Handles PUT requests."""
    user = self.VerifyPermissions(permissions.ESCROW)
    self.VerifyXsrfToken(base_settings.SET_PASSPHRASE_ACTION)

    key_pair = self.GetSecretFromBody()
    if volume_uuid and key_pair:
      if not self.IsSaneUuid(volume_uuid):
        raise models.DuplicityAccessError(
            'volume_uuid is malformed: %r' % volume_uuid, self.request)

      self.PutNewKeyPair(user.email, volume_uuid, key_pair, self.request)
    else:
      self.AUDIT_LOG_MODEL.Log(message='Unknown PUT', request=self.request)
      self.error(400)

  def PutNewKeyPair(self, owner, volume_uuid, key_pair, metadata):
    """Puts a new DuplicityKeyPair entity to Datastore.

    Args:
      owner: str, email address of the key pair's owner.
      volume_uuid: str, backup volume UUID associated with this key pair.
      key_pair: str, ASCII armored key pair.
      metadata: dict, dict of str metadata with keys matching
          models.DuplicityKeyPair property names.
    """
    entity = models.DuplicityKeyPair(
        key_pair=str(key_pair),
        key_name=volume_uuid,
        owner=owner,
        volume_uuid=volume_uuid)

    for prop_name in entity.properties():
      value = metadata.get(prop_name)
      if value:
        setattr(entity, prop_name, self.SanitizeString(value))

    entity.put()

    self.AUDIT_LOG_MODEL.Log(entity=entity, message='PUT', request=self.request)

    self.response.out.write('Key pair successfully escrowed!')
