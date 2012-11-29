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

from cauliflowervest import settings as base_settings
from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util

# Prefix to prevent Cross Site Script Inclusion.
JSON_PREFIX = ")]}',\n"


class FileVault(handlers.FileVaultAccessHandler):
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
        'helpdesk_email': settings.HELPDESK_EMAIL,
        }
    user_email = user.user.email()
    try:
      # If the user has access to "silently" retrieve keys without the owner
      # being notified, email only SILENT_AUDIT_ADDRESSES.
      self.VerifyPermissions(permissions.SILENT_RETRIEVE, user)
      to = [user_email] + settings.SILENT_AUDIT_ADDRESSES
    except models.AccessDeniedError:
      # Otherwise email the owner and RETRIEVE_AUDIT_ADDRESSES.
      owner_email = '%s@%s' % (entity.owner, settings.DEFAULT_EMAIL_DOMAIN)
      to = [owner_email, user_email] + settings.RETRIEVE_AUDIT_ADDRESSES

    # In case of empty owner.
    to = [x for x in to if x]

    util.SendEmail(to, settings.RETRIEVAL_EMAIL_SUBJECT, body)

  def RetrievePassphrase(self, volume_uuid):
    """Handles a GET request to retrieve a passphrase."""
    try:
      self.VerifyXsrfToken(base_settings.GET_PASSPHRASE_ACTION)
    except models.AccessDeniedError as er:
      # Send the exception message for non-JSON requests.
      if self.request.get('json', '1') == '0':
        self.response.out.write(str(er))
        return
      raise
    user = self.VerifyPermissions(permissions.RETRIEVE)
    entity = models.FileVaultVolume.get_by_key_name(volume_uuid)
    if not entity:
      raise models.FileVaultAccessError(
          'volume_uuid not found: %s' % volume_uuid, self.request)

    models.FileVaultAccessLog.Log(
        message='GET', entity=entity, request=self.request)

    self.SendRetrievalEmail(entity, user)
    if self.request.get('json', '1') == '0':
      # Make escrow secret a str with no trailing spaces
      escrow_secret = str(entity.passphrase).strip()
      # Convert str to barcode compatible secret
      escrow_barcode_secret = escrow_secret.replace('-', '')
      params = {'escrow_secret': escrow_secret,
                'escrow_barcode_secret': escrow_barcode_secret}
      self.RenderTemplate('barcode_result.html', params)
    else:
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

    self.VerifyXsrfToken(base_settings.SET_PASSPHRASE_ACTION)

    if volume_uuid and self.request.body:
      recovery_token = self.request.body
      if recovery_token[-1] == '=':
        # Work around a client/server bug which causes a stray '=' to be added
        # to the request body when a form-encoded content type is sent.
        recovery_token = recovery_token[0:-1]

      if not self.IsSaneUuid(volume_uuid):
        raise models.FileVaultAccessError('volume_uuid is malformed')

      if not self.IsSaneUuid(recovery_token):
        raise models.FileVaultAccessError('recovery key is malformed')

      self.PutNewPassphrase(volume_uuid, recovery_token, self.request)
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