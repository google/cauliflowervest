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

"""Module to handle interaction with a FileVault."""




import json

from google.appengine.ext import webapp

from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util

# Prefix to prevent Cross Site Script Inclusion.
JSON_PREFIX = ")]}',\n"


class FileVault(handlers.FileVaultAccessHandler, webapp.RequestHandler):
  """Handler for /filevault URL."""

  def SendRetrievalEmail(self, entity, user):
    """Sends a retrieval notification email to the owner of a Mac.

    Args:
      entity: models.FileVaultVolume object that was retrieved.
      user: models.User object of the user that retrieved the passphrase.
    """
    body = settings.RETRIEVAL_EMAIL_BODY % {
        'retrieved_by': user.user.email(),
        'hostname': entity.hostname,
        'platform_uuid': entity.platform_uuid,
        'serial': entity.serial or '',
        'hdd_serial': entity.hdd_serial,
        'volume_uuid': entity.volume_uuid,
        'helpdesk_name': settings.HELPDESK_NAME,
        }
    user_email = user.user.email()
    try:
      # If the user has access to "silently" retrieve keys without the owner
      # being notified, email only SILENT_AUDIT_ADDRESSES.
      self.VerifyPermissions(permissions.SILENT_RETRIEVE, user)
      to = [user_email] + settings.SILENT_AUDIT_ADDRESSES
    except models.FileVaultAccessDeniedError:
      # Otherwise email the owner and RETRIEVE_AUDIT_ADDRESSES.
      owner_email = '%s@%s' % (entity.owner, settings.DEFAULT_EMAIL_DOMAIN)
      to = [owner_email, user_email] + settings.RETRIEVE_AUDIT_ADDRESSES

    # In case of empty owner.
    to = [x for x in to if x]

    util.SendEmail(to, settings.RETRIEVAL_EMAIL_SUBJECT, body)

  def RetrievePassphrase(self, volume_uuid):
    """Handles a GET request to retrieve a passphrase."""
    # TODO(user): Enforce presence of XSRF token here.
    # Without this, XSRF requests can trigger emails (but not retreive tokens).
    user = self.VerifyPermissions(permissions.RETRIEVE)
    entity = models.FileVaultVolume.get_by_key_name(volume_uuid)
    if not entity:
      raise models.FileVaultAccessError(
          'volume_uuid not found: %s' % volume_uuid, self.request)

    models.FileVaultAccessLog.Log(
        message='GET', entity=entity, request=self.request)

    self.SendRetrievalEmail(entity, user)

    data = {'passphrase': entity.passphrase}
    self.response.out.write(JSON_PREFIX + json.dumps(data))

  def VerifyEscrow(self, volume_uuid):
    """Handles a GET to verify if a volume uuid has an escrowed passphrase."""
    self.VerifyDomainUser()
    entity = models.FileVaultVolume.get_by_key_name(volume_uuid)
    if not entity:
      self.error(404)
    else:
      self.response.out.write('Escrow verified.')

  # pylint: disable-msg=C6409
  def get(self, volume_uuid=None):
    """Handles GET requests."""
    if not volume_uuid:
      raise models.FileVaultAccessError('volume_uuid is required', self.request)

    if not self.IsSaneUuid(volume_uuid):
      raise models.FileVaultAccessError('volume_uuid is malformed')

    if self.request.get('only_verify_escrow'):
      self.VerifyEscrow(volume_uuid)
    else:
      self.RetrievePassphrase(volume_uuid)

  # pylint: disable-msg=C6409
  def put(self, volume_uuid=None):
    """Handles PUT requests."""
    if settings.ALLOW_ALL_DOMAIN_USERS_TO_ESCROW:
      self.VerifyDomainUser()
    else:
      self.VerifyPermissions(permissions.ESCROW)

    if not self.IsSaneUuid(volume_uuid):
      raise models.FileVaultAccessError('volume_uuid is malformed')

    if not self.IsSaneUuid(self.request.body):
      raise models.FileVaultAccessError('recovery key is malformed')

    if volume_uuid and self.request.body:
      self.PutNewPassphrase(volume_uuid, self.request.body, self.request)
    else:
      models.FileVaultAccessLog.Log(
          message='Unknown PUT', request=self.request)
      self.error(400)

  def PutNewPassphrase(self, volume_uuid, passphrase, metadata):
    """Puts a new FileVaultVolume entity to Datastore.

    Args:
      volume_uuid: str, Volume UUID associated to the passphrase to put.
      passphrase: str, FileVault2 passphrase / recovery token.
      metadata: dict, dict of str metadata with keys matching
          models.FileVaultVolume property names.
    """
    # TODO(user): Enforce presence of XSRF token here.
    # Without this, XSRF requests can create bogus extra records.

    if not volume_uuid:
      raise models.FileVaultAccessError('volume_uuid is required', self.request)

    entity = models.FileVaultVolume(
        key_name=volume_uuid,
        volume_uuid=volume_uuid,
        passphrase=str(passphrase))

    for prop_name in entity.properties():
      value = metadata.get(prop_name)
      if value:
        setattr(entity, prop_name, self.SanitizeString(value))

    entity.put()

    models.FileVaultAccessLog.Log(
        entity=entity, message='PUT', request=self.request)

    self.response.out.write('Passphrase successfully escrowed!')