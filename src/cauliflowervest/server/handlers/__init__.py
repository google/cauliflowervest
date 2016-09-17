#!/usr/bin/env python
"""Top level __init__ for handlers package."""

import base64
import cgi
import httplib
import logging
import os
import re
import StringIO
import sys
import traceback
import urllib

import webapp2

from google.appengine.api import app_identity
from google.appengine.api import datastore_errors
from google.appengine.ext import db

from cauliflowervest import settings as base_settings
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util


class InvalidArgumentError(models.Error):
  """One of argument has invalid value or missing."""
  error_code = httplib.BAD_REQUEST


def VerifyPermissions(required_permission, user, permission_type):
  """Verifies a valid user is logged in.

  Args:
    required_permission: permission string from permissions.*.
    user: models.User entity; default current user.
    permission_type: string, one of permission.TYPE_* variables.
  Raises:
    models.AccessDeniedError: there was a permissions issue.
  """
  if not permission_type:
    raise models.AccessDeniedError('permission_type not specified')

  try:
    if not user.HasPerm(required_permission, permission_type=permission_type):
      raise models.AccessDeniedError(
          'User lacks %s permission' % required_permission)
  except ValueError:
    raise models.AccessDeniedError(
        'unknown permission_type: %s' % permission_type)


def VerifyAllPermissionTypes(required_permission, user=None):
  """Verifies if a user has the required_permission for all permission types.

  Args:
    required_permission: permission string from permissions.*.
    user: optional, models.User entity; default current user.
  Returns:
    Dict. Keys are permissions.TYPES values, and value booleans, True when
    the user has the required_permission for the permission type, False
    otherwise.
  """
  if user is None:
    user = models.GetCurrentUser()

  perms = {}
  for permission_type in permissions.TYPES:
    try:
      VerifyPermissions(required_permission, user, permission_type)
      perms[permission_type] = True
    except models.AccessDeniedError:
      perms[permission_type] = False
  # TODO(user): if use of this method widens, consider returning a
  #    collections.namedtuple instead of a basic dict.
  return perms


def SendRetrievalEmail(
    permission_type, entity, user, template='retrieval_email.txt',
    skip_emails=None):
  """Sends a retrieval notification email.

  Args:
    permission_type: string, one of permission.TYPE_* variables.
    entity: models instance of retrieved object.  (E.G. FileVaultVolume,
        DuplicityKeyPair, BitLockerVolume, etc.)
    user: models.User object of the user that retrieved the secret.
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
    # If the user has access to "silently" retrieve keys without the owner
    # being notified, email only SILENT_AUDIT_ADDRESSES.
    VerifyPermissions(permissions.SILENT_RETRIEVE, user, permission_type)
    to = [user_email] + settings.SILENT_AUDIT_ADDRESSES
  except models.AccessDeniedError:
    # Otherwise email the owner and RETRIEVE_AUDIT_ADDRESSES.
    to = [user_email] + settings.RETRIEVE_AUDIT_ADDRESSES
    if entity.owner:
      if '@' in entity.owner:
        owner_email = entity.owner
      else:
        owner_email = '%s@%s' % (entity.owner, settings.DEFAULT_EMAIL_DOMAIN)
      to.append(owner_email)

  if skip_emails:
    to = [email for email in to if email not in skip_emails]

  subject_var = '%s_RETRIEVAL_EMAIL_SUBJECT' % entity.ESCROW_TYPE_NAME.upper()
  subject = getattr(
      settings, subject_var, 'Escrow secret retrieval notification.')
  util.SendEmail(to, subject, body)


class AccessHandler(webapp2.RequestHandler):
  """Class which handles AccessError exceptions."""

  AUDIT_LOG_MODEL = models.AccessLog
  JSON_SECRET_NAME = 'passphrase'
  PERMISSION_TYPE = 'base'
  UUID_REGEX = None

  def get(self, volume_uuid):
    """Handles GET requests."""
    if not self.IsValidUuid(volume_uuid):
      raise models.AccessError('volume_uuid is malformed')

    self.RetrieveSecret(volume_uuid)

  def put(self, volume_uuid=None):
    """Handles PUT requests."""
    if not volume_uuid:
      volume_uuid = self.request.get('volume_uuid')

    user = self.VerifyPermissions(permissions.ESCROW)
    self.VerifyXsrfToken(base_settings.SET_PASSPHRASE_ACTION)

    if not self.IsValidUuid(volume_uuid):
      raise models.AccessError('volume_uuid is malformed')

    secret = self.GetSecretFromBody()
    if not volume_uuid or not secret:
      self.AUDIT_LOG_MODEL.Log(message='Unknown PUT', request=self.request)
      self.error(httplib.BAD_REQUEST)
      return
    if not self.IsValidSecret(secret):
      raise models.AccessError('secret is malformed')

    owner = self.SanitizeEntityValue('owner', self.request.get('owner'))
    owner = owner or user.email
    self.PutNewSecret(owner, volume_uuid, secret, self.request)

  def _CreateNewSecretEntity(self, *args):
    raise NotImplementedError()

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
    return True

  def IsValidUuid(self, uuid):
    """Returns true if uuid str is a well formatted uuid."""
    if self.UUID_REGEX is None:
      return True
    return self.UUID_REGEX.search(uuid) is not None

  def PutNewSecret(self, owner, volume_uuid, secret, metadata):
    """Puts a new DuplicityKeyPair entity to Datastore.

    Args:
      owner: str, email address of the key pair's owner.
      volume_uuid: str, backup volume UUID associated with this key pair.
      secret: str, secret data to escrow.
      metadata: dict, dict of str metadata with keys matching
          models.DuplicityKeyPair property names.
    """
    if not volume_uuid:
      raise models.AccessError('volume_uuid is required')

    entity = self._CreateNewSecretEntity(owner, volume_uuid, secret)
    for prop_name in entity.properties():
      value = metadata.get(prop_name)
      if value:
        setattr(entity, prop_name, self.SanitizeEntityValue(prop_name, value))

    try:
      entity.put()
      self.AUDIT_LOG_MODEL.Log(
          entity=entity, message='PUT', request=self.request)
    except models.DuplicateEntity:
      logging.info('New entity duplicate active volume with same uuid.')

    self.response.out.write('Secret successfully escrowed!')

  def CheckRetrieveAuthorization(self, entity, user):
    """Checks whether the user is authorised to retrieve the secret.

    Args:
      entity: models instance of retrieved object.  (E.G. FileVaultVolume,
          DuplicityKeyPair, BitLockerVolume, etc.)
      user: models.User object of the user that retrieved the secret.
    Returns:
      models.User object of the current user.
    Raises:
      models.AccessDeniedError: user lacks any retrieval permissions.
      models.AccessError: user lacks a specific retrieval permission.
    """
    try:
      self.VerifyPermissions(permissions.RETRIEVE, user=user)
    except models.AccessDeniedError:
      try:
        self.VerifyPermissions(permissions.RETRIEVE_CREATED_BY, user=user)
        if str(entity.created_by) not in str(user.user.email()):
          raise
      except models.AccessDeniedError:
        self.VerifyPermissions(permissions.RETRIEVE_OWN, user=user)
        if entity.owner not in (user.email, user.user.nickname()):
          raise

    return user

  def RetrieveSecret(self, volume_uuid):
    """Handles a GET request to retrieve a secret."""
    self.VerifyXsrfToken(base_settings.GET_PASSPHRASE_ACTION)

    if self.request.get('id'):
      try:
        entity = self.SECRET_MODEL.get(db.Key(self.request.get('id')))
      except datastore_errors.BadKeyError:
        raise models.AccessError('volume id is malformed')
    else:
      entity = self.SECRET_MODEL.GetLatestByUuid(
          volume_uuid, tag=self.request.get('tag', 'default'))

    if not entity:
      raise models.AccessError('Volume not found: %s' % volume_uuid)

    user = models.GetCurrentUser()

    self.CheckRetrieveAuthorization(entity=entity, user=user)

    self.AUDIT_LOG_MODEL.Log(message='GET', entity=entity, request=self.request)

    # Send retrieval email if user is not retrieving their own secret.
    if entity.owner not in (user.user.email(), user.user.nickname()):
      SendRetrievalEmail(self.PERMISSION_TYPE, entity, user)

    escrow_secret = str(entity.secret).strip()
    if isinstance(entity, models.ProvisioningVolume):
      # We don't want to display barcodes for users retrieving provisioning
      # passwords as seeing the barcodes frightens and confuses them.
      escrow_barcode_svg = None
      qr_img_url = None
    else:
      escrow_barcode_svg = None
      if len(escrow_secret) <= 100:
        qr_img_url = (
            'https://chart.googleapis.com/chart?chs=245x245&cht=qr&chl='
            + cgi.escape(escrow_secret))
      else:
        qr_img_url = None

    if entity.ESCROW_TYPE_NAME == models.ProvisioningVolume.ESCROW_TYPE_NAME:
      recovery_str = 'Temporary password'
    else:
      recovery_str = '%s key' % entity.ESCROW_TYPE_NAME

    params = {
        'volume_type': self.SECRET_MODEL.ESCROW_TYPE_NAME,
        'volume_uuid': entity.volume_uuid,
        'qr_img_url': qr_img_url,
        'escrow_secret': escrow_secret,
        'checksum': entity.checksum,
        'recovery_str': recovery_str,
    }

    params[self.JSON_SECRET_NAME] = escrow_secret
    self.response.out.write(util.ToSafeJson(params))

  def SanitizeEntityValue(self, unused_prop_name, value):
    if value is not None:
      return cgi.escape(value)

  def VerifyPermissions(
      self, required_permission, user=None, permission_type=None):
    """Verifies a valid user is logged in.

    Args:
      required_permission: permission string from permissions.*.
      user: optional, models.User entity; default current user.
      permission_type: optional, string, one of permission.TYPE_* variables. if
          omitted, self.PERMISSION_TYPE is used.
    Returns:
      models.User object of the current user.
    Raises:
      models.AccessDeniedError: there was a permissions issue.
    """
    # TODO(user): Consider making the method accept a list of checks
    #    to be performed, making CheckRetrieveAuthorization simpler.
    permission_type = permission_type or self.PERMISSION_TYPE

    if user is None:
      user = models.GetCurrentUser()

    VerifyPermissions(required_permission, user, permission_type)

    return user

  def VerifyXsrfToken(self, action):
    """Verifies a valid XSRF token was passed for the current request.

    Args:
      action: String, validate the token against this action.
    Returns:
      Boolean. True if the XSRF Token was valid.
    Raises:
      models.AccessDeniedError: the XSRF token was invalid or not supplied.
    """
    xsrf_token = self.request.get('xsrf-token', None)
    if settings.XSRF_PROTECTION_ENABLED:
      if not util.XsrfTokenValidate(xsrf_token, action):
        raise models.AccessDeniedError('Valid XSRF token not provided')
    elif not xsrf_token:
      logging.info(
          'Ignoring missing XSRF token; settings.XSRF_PROTECTION_ENABLED=False')
    return True

  # pylint: disable=g-bad-name
  def handle_exception(self, exception, debug_mode):
    """Handle an exception.

    Args:
      exception: exception that was thrown
      debug_mode: True if the application is running in debug mode
    """
    if issubclass(exception.__class__, models.Error):
      self.AUDIT_LOG_MODEL.Log(
          successful=False, message=exception.message, request=self.request)

      exc_type, exc_value, exc_tb = sys.exc_info()
      tb = traceback.format_exception(exc_type, exc_value, exc_tb)
      logging.warning('handle_exception: %s', ''.join(tb))

      self.error(exception.error_code)
      if issubclass(exception.__class__, models.AccessDeniedError):
        self.response.out.write('Access denied.')
      else:
        self.response.out.write(cgi.escape(exception.message))
    else:
      super(AccessHandler, self).handle_exception(exception, debug_mode)


class BitLockerAccessHandler(AccessHandler):
  """Class which handles BitLocker handler."""
  AUDIT_LOG_MODEL = models.BitLockerAccessLog
  SECRET_MODEL = models.BitLockerVolume
  PERMISSION_TYPE = permissions.TYPE_BITLOCKER


class DuplicityAccessHandler(AccessHandler):
  """Class which handles Luks keys handler."""
  AUDIT_LOG_MODEL = models.DuplicityAccessLog
  SECRET_MODEL = models.DuplicityKeyPair
  PERMISSION_TYPE = permissions.TYPE_DUPLICITY


class FileVaultAccessHandler(AccessHandler):
  """Class which handles File vault handler."""
  AUDIT_LOG_MODEL = models.FileVaultAccessLog
  SECRET_MODEL = models.FileVaultVolume
  PERMISSION_TYPE = permissions.TYPE_FILEVAULT


class LuksAccessHandler(AccessHandler):
  """Class which handles Luks keys handler."""
  AUDIT_LOG_MODEL = models.LuksAccessLog
  SECRET_MODEL = models.LuksVolume
  PERMISSION_TYPE = permissions.TYPE_LUKS


class ProvisioningAccessHandler(AccessHandler):
  """Class which handles Provisioning keys handler."""
  AUDIT_LOG_MODEL = models.ProvisioningAccessLog
  SECRET_MODEL = models.ProvisioningVolume
  PERMISSION_TYPE = permissions.TYPE_PROVISIONING
