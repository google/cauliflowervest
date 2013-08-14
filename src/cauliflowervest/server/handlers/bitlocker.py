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

"""Module to handle interaction with a BitLocker."""




import datetime
import logging

from cauliflowervest import settings as base_settings
from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import settings

# Prefix to prevent Cross Site Script Inclusion.
JSON_PREFIX = ")]}',\n"


class BitLocker(handlers.BitLockerAccessHandler):
  """Handler for /bitlocker URL."""

  def VerifyKey(self, volume_uuid):
    """Handles a GET to verify if a volume_uuid has a key."""
    self.VerifyPermissions(permissions.ESCROW)
    entity = models.BitLockerVolume.get_by_key_name(volume_uuid)
    if not entity:
      self.error(404)
    else:
      self.response.out.write('key verified.')


  def get(self, volume_uuid=None):  # pylint: disable=g-bad-name
    """Handles GET requests."""
    if not volume_uuid:
      raise models.BitLockerAccessError('volume_uuid is required', self.request)

    volume_uuid = volume_uuid.upper()
    if self.request.get('only_verify_escrow'):
      self.VerifyKey(volume_uuid)
    else:
      self.RetrieveSecret(volume_uuid)

  def put(self, volume_uuid=None):  # pylint: disable=g-bad-name
    """Handles PUT requests."""
    self.VerifyPermissions(permissions.ESCROW)
    self.VerifyXsrfToken(base_settings.SET_PASSPHRASE_ACTION)
    if self.request.body:
      recovery_key = self.request.body
      self.PutNewRecoveryKey(volume_uuid, recovery_key, self.request)
    else:
      self.AUDIT_LOG_MODEL.Log(message='Unknown PUT', request=self.request)
      self.error(400)

  def PutNewRecoveryKey(self, volume_uuid, recovery_key, metadata):
    """Puts a new BitLockerVolume entity to Datastore.

    Args:
      volume_uuid: str, volume UUID associated to the recovery_key to put.
      recovery_key: str, BitLocker recovery token.
      metadata: dict, dict of str metadata with keys matching
          models.BitLockerVolume property names.
    """
    if not volume_uuid:
      raise models.BitLockerAccessError('volume_uuid is required', self.request)

    volume_uuid = volume_uuid.upper()
    entity = models.BitLockerVolume(
        key_name=volume_uuid,
        volume_uuid=volume_uuid,
        recovery_key=str(recovery_key))
    for prop_name in entity.properties():
      value = metadata.get(prop_name)
      if value:
        if prop_name == 'when_created':
          value = value.strip()
          try:
            value = datetime.datetime.strptime(value, '%Y%m%d%H%M%S.0Z')
          except ValueError:
            logging.error('Uknown when_created format: %r', value)
            value = None
        else:
          value = self.SanitizeString(value)
        setattr(entity, prop_name, value)
    entity.put()

    self.AUDIT_LOG_MODEL.Log(entity=entity, message='PUT', request=self.request)

    self.response.out.write('Recovery successfully escrowed!')
