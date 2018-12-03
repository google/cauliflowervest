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

"""Base class for passphrase upload/retrieval handlers."""
import base64
import cgi
import httplib
import logging
import StringIO



from google.appengine.api import app_identity
from google.appengine.api import datastore_errors
from google.appengine.ext import db

from cauliflowervest import settings as base_settings
from cauliflowervest.server import permissions
from cauliflowervest.server import service_factory
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.models import base
from cauliflowervest.server.models import errors


class InvalidArgumentError(errors.Error):
  """One of argument has invalid value or missing."""
  error_code = httplib.BAD_REQUEST


def SendRetrievalEmail(
    permission_type, entity, user, template='retrieval_email.txt',
    skip_emails=None):
  """Sends a retrieval notification email.

  Args:
    permission_type: string, one of permission.TYPE_* variables.
    entity: base.BasePassphrase instance of retrieved object.
    user: base.User object of the user that retrieved the secret.
    template: str message template.
    skip_emails: list filter emails from recipients.
  """
  data = {
      'entity': entity,
      'helpdesk_email': settings.HELPDESK_EMAIL,
      'helpdesk_name': settings.HELPDESK_NAME,
      'retrieved_by': user.user.email(),
      'user': user,
      'server_hostname': app_identity.get_default_version_hostname(),
  }
  body = util.RenderTemplate(template, data)

  user_email = user.user.email()
  try:
    base_handler.VerifyPermissions(
        permissions.SILENT_RETRIEVE, user, permission_type)
    return
  except errors.AccessDeniedError:
    pass

  try:
    # If the user has access to "silently" retrieve keys without the owner
    # being notified, email only SILENT_AUDIT_ADDRESSES.
    base_handler.VerifyPermissions(
        permissions.SILENT_RETRIEVE_WITH_AUDIT_EMAIL, user, permission_type)
    to = [user_email] + settings.SILENT_AUDIT_ADDRESSES
  except errors.AccessDeniedError:
    # Otherwise email the owner and RETRIEVE_AUDIT_ADDRESSES.
    to = [user_email] + settings.RETRIEVE_AUDIT_ADDRESSES

    if entity.owners:
      to.extend(entity.owners)

  if skip_emails:
    to = [email for email in to if email not in skip_emails]

  subject_var = '%s_RETRIEVAL_EMAIL_SUBJECT' % entity.ESCROW_TYPE_NAME.upper()
  subject = getattr(
      settings, subject_var, 'Escrow secret retrieval notification.')
  util.SendEmail(to, subject, body)


class PassphraseHandler(base_handler.BaseHandler):
  """Class which handles passphrase upload/retrieval."""

  JSON_SECRET_NAME = 'passphrase'
  PERMISSION_TYPE = 'base'
  TARGET_ID_REGEX = None
  SECRET_REGEX = None

  QRCODE_DURING_PASSPHRASE_RETRIEVAL = True

  def get(self, target_id):
    """Handles GET requests."""
    if not self.IsValidTargetId(target_id):
      raise errors.AccessError('target_id is malformed')

    self.RetrieveSecret(target_id)

  def put(self, target_id=None):
    """Handles PUT requests."""
    if not target_id:
      target_id = self.request.get('volume_uuid')

    email = self._VerifyEscrowPermission()

    self.VerifyXsrfToken(base_settings.SET_PASSPHRASE_ACTION)

    if not self.IsValidTargetId(target_id):
      raise errors.AccessError('target_id is malformed')

    secret = self.GetSecretFromBody()
    if not target_id or not secret:
      self.AUDIT_LOG_MODEL.Log(message='Unknown PUT', request=self.request)
      self.error(httplib.BAD_REQUEST)
      return
    if not self.IsValidSecret(secret):
      raise errors.AccessError('secret is malformed')

    owner = self.SanitizeEntityValue('owner', self.request.get('owner'))
    if email:
      owner = owner or email
    self.PutNewSecret(owner, target_id, secret, self.request)

  def _CreateNewSecretEntity(self, *args):
    raise NotImplementedError()

  def _VerifyEscrowPermission(self):
    """Returns user object or None."""
    user = self.VerifyPermissions(permissions.ESCROW)
    return user.email

  def GetSecretFromBody(self):
    """Returns the uploaded secret from a PUT or POST request."""
    secret = self.request.body
    if not secret:
      return None

    # Work around a client/server bug which causes a stray '=' to be added
    # to the request body when a form-encoded content type is sent.
    if (self.request.content_type ==
        'application/x-www-form-urlencoded' and secret[-1] == '='):
      return secret[:-1]
    else:
      return secret

  def IsValidSecret(self, unused_secret):
    """Returns true if secret str is a well formatted."""
    return True

  def IsValidTargetId(self, target_id):
    """Returns true if target_id str is a well formatted."""
    if self.TARGET_ID_REGEX is None:
      return True
    return self.TARGET_ID_REGEX.match(target_id) is not None

  def PutNewSecret(self, owner, target_id, secret, metadata):
    """Puts a new DuplicityKeyPair entity to Datastore.

    Args:
      owner: str, email address of the key pair's owner.
      target_id: str, target id associated with this passphrase.
      secret: str, secret data to escrow.
      metadata: dict, dict of str metadata with keys matching
          model's property names.
    """
    if not target_id:
      raise errors.AccessError('target_id is required')

    entity = self._CreateNewSecretEntity(owner, target_id, secret)
    for prop_name in entity.properties():
      value = metadata.get(prop_name)
      if value:
        setattr(entity, prop_name, self.SanitizeEntityValue(prop_name, value))

    inventory = service_factory.GetInventoryService()
    inventory.FillInventoryServicePropertiesDuringEscrow(
        entity, self.request)
    for k, v in inventory.GetMetadataUpdates(entity).items():
      setattr(entity, k, v)

    try:
      entity.put()
    except errors.DuplicateEntity:
      logging.info('Same data already in datastore.')
    else:
      self.AUDIT_LOG_MODEL.Log(
          entity=entity, message='PUT', request=self.request)

    self.response.out.write('Secret successfully escrowed!')

  def CheckRetrieveAuthorizationAndNotifyOwner(self, entity):
    """Checks whether the user is authorised to retrieve the secret.

    Args:
      entity: base.BasePassPhrase instance of retrieved object.
    Raises:
      errors.AccessDeniedError: user lacks any retrieval permissions.
      errors.AccessError: user lacks a specific retrieval permission.
    """
    user = base.GetCurrentUser()

    try:
      self.VerifyPermissions(permissions.RETRIEVE, user=user)
    except errors.AccessDeniedError:
      try:
        self.VerifyPermissions(permissions.RETRIEVE_CREATED_BY, user=user)
        if str(entity.created_by) not in str(user.user.email()):
          raise
      except errors.AccessDeniedError:
        self.VerifyPermissions(permissions.RETRIEVE_OWN, user=user)
        if user.email not in entity.owners:
          raise

    if user.email not in entity.owners:
      SendRetrievalEmail(self.PERMISSION_TYPE, entity, user)

  def RetrieveSecret(self, target_id):
    """Handles a GET request to retrieve a secret.

    Args:
      target_id: str, Target ID to fetch the secret for.
    Raises:
      base.AccessError: given target_id is malformed.
      base.NotFoundError: no secret was found for the given target_id.
    """
    self.VerifyXsrfToken(base_settings.GET_PASSPHRASE_ACTION)

    if self.request.get('id'):
      try:
        entity = self.SECRET_MODEL.get(db.Key(self.request.get('id')))
      except datastore_errors.BadKeyError:
        raise errors.AccessError('target_id is malformed')
    else:
      entity = self.SECRET_MODEL.GetLatestForTarget(
          target_id, tag=self.request.get('tag', 'default'))

    if not entity:
      raise errors.NotFoundError(
          'Passphrase not found: target_id %s' % target_id)

    self.CheckRetrieveAuthorizationAndNotifyOwner(entity=entity)

    self.AUDIT_LOG_MODEL.Log(message='GET', entity=entity, request=self.request)

    escrow_secret = str(entity.secret).strip()

    escrow_barcode_svg = None
    qr_img_url = None
    if self.QRCODE_DURING_PASSPHRASE_RETRIEVAL:
      if len(escrow_secret) <= 100:
        qr_img_url = (
            'https://chart.googleapis.com/chart?chs=245x245&cht=qr&chl='
            + cgi.escape(escrow_secret))

    recovery_str = self._PassphraseTypeName(entity)

    params = {
        'volume_type': self.SECRET_MODEL.ESCROW_TYPE_NAME,
        'volume_uuid': entity.target_id,
        'qr_img_url': qr_img_url,
        'escrow_secret': escrow_secret,
        'checksum': entity.checksum,
        'recovery_str': recovery_str,
    }

    params[self.JSON_SECRET_NAME] = escrow_secret

    if entity.active:
      entity.UpdateMutableProperty('force_rekeying', True)

    self.response.out.write(util.ToSafeJson(params))

  def _PassphraseTypeName(self, entity):
    return '%s key' % entity.ESCROW_TYPE_NAME

  def SanitizeEntityValue(self, unused_prop_name, value):
    if value is not None:
      return cgi.escape(value)

  def VerifyPermissions(
      self, required_permission, user=None, permission_type=None):
    """Verifies a valid user is logged in.

    Args:
      required_permission: permission string from permissions.*.
      user: optional, base.User entity; default current user.
      permission_type: optional, string, one of permission.TYPE_* variables. if
          omitted, self.PERMISSION_TYPE is used.
    Returns:
      base.User object of the current user.
    Raises:
      errors.AccessDeniedError: there was a permissions issue.
    """
    permission_type = permission_type or self.PERMISSION_TYPE

    if user is None:
      user = base.GetCurrentUser()

    base_handler.VerifyPermissions(required_permission, user, permission_type)

    return user
