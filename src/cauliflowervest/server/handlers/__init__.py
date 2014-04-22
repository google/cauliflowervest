#!/usr/bin/env python
#
# Copyright 2011 Google Inc. All Rights Reserved.

"""Top level __init__ for handlers package."""

import base64
import cgi
import json
import logging
import os
import re
import StringIO
import sys
import traceback

import webapp2

from google.appengine.ext.webapp import template

from cauliflowervest import settings as base_settings
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates')
# TODO(user): Move this into base_settings so it is shared between clients
# and servers.
JSON_PREFIX = ")]}',\n"


class AccessHandler(webapp2.RequestHandler):
  """Class which handles AccessError exceptions."""

  AUDIT_LOG_MODEL = models.AccessLog
  JSON_SECRET_NAME = 'passphrase'
  PERMISSION_TYPE = 'base'
  UUID_REGEX = None

  def get(self, volume_uuid=None):  # pylint: disable=g-bad-name
    """Handles GET requests."""
    if not volume_uuid:
      raise models.AccessError('volume_uuid is required')

    if not self.IsValidUuid(volume_uuid):
      raise models.AccessError('volume_uuid is malformed')

    if self.request.get('only_verify_escrow'):
      self.VerifyEscrow(volume_uuid)
    else:
      self.RetrieveSecret(volume_uuid)

  def put(self, volume_uuid=None):  # pylint: disable=g-bad-name
    """Handles PUT requests."""
    user = self.VerifyPermissions(permissions.ESCROW)
    self.VerifyXsrfToken(base_settings.SET_PASSPHRASE_ACTION)

    if not self.IsValidUuid(volume_uuid):
      raise models.AccessError('volume_uuid is malformed')

    secret = self.GetSecretFromBody()
    if not volume_uuid or not secret:
      self.AUDIT_LOG_MODEL.Log(message='Unknown PUT', request=self.request)
      self.error(400)
      return
    if not self.IsValidSecret(secret):
      raise models.AccessError('secret is malformed')

    self.PutNewSecret(user.email, volume_uuid, secret, self.request)

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

    entity.put()

    self.AUDIT_LOG_MODEL.Log(entity=entity, message='PUT', request=self.request)

    self.response.out.write('Secret successfully escrowed!')

  def RenderTemplate(self, template_path, params, response_out=True):
    """Renders a template of a given path and optionally writes to response.

    Args:
      template_path: str, template name or relative path to the base template
          dir as defined in settings.
      params: dictionary, key/values to send to the template.render().
      response_out: boolean, True to write to self.response.out(), False to
          simply return the rendered HTML str.
    Returns:
      String rendered HTML if response_out == False, otherwise None.
    """
    user = models.GetCurrentUser()
    params['user'] = user
    html = template.render(os.path.join(TEMPLATE_DIR, template_path), params)
    if response_out:
      self.response.out.write(html)
    else:
      return html

  def RetrieveSecret(self, secret_id):
    """Handles a GET request to retrieve a secret."""
    try:
      self.VerifyXsrfToken(base_settings.GET_PASSPHRASE_ACTION)
    except models.AccessDeniedError as er:
      # Send the exception message for non-JSON requests.
      if self.request.get('json', '1') == '0':
        self.response.out.write(str(er))
        return
      raise

    user = models.GetCurrentUser()
    try:
      self.VerifyPermissions(permissions.RETRIEVE, user=user)
      verify_owner = False
    except models.AccessDeniedError:
      self.VerifyPermissions(permissions.RETRIEVE_OWN, user=user)
      verify_owner = True

    entity = self.SECRET_MODEL.get_by_key_name(secret_id)
    if not entity:
      raise models.AccessError('Secret not found: %s' % secret_id)

    if verify_owner:
      if entity.owner not in (user.email, user.user.nickname()):
        raise models.AccessError(
            'Attempt to access unowned secret: %s' % secret_id)

    self.AUDIT_LOG_MODEL.Log(message='GET', entity=entity, request=self.request)

    self.SendRetrievalEmail(entity, user)

    escrow_secret = str(entity.passphrase).strip()
    if self.request.get('json', '1') == '0':
      escrow_barcode_svg = None
      if len(escrow_secret) <= 100:
        qr_img_url = (
            'https://chart.googleapis.com/chart?chs=245x245&cht=qr&chl='
            + cgi.escape(escrow_secret))
      else:
        qr_img_url = None
      params = {
          'escrow_secret': escrow_secret,
          'qr_img_url': qr_img_url,
          }
      self.RenderTemplate('barcode_result.html', params)
    else:
      data = {self.JSON_SECRET_NAME: escrow_secret}
      self.response.out.write(JSON_PREFIX + json.dumps(data))

  def SanitizeEntityValue(self, unused_prop_name, value):
    return cgi.escape(value)

  def SendRetrievalEmail(self, entity, user):
    """Sends a retrieval notification email.

    Args:
      entity: models instance of retrieved object.  (E.G. FileVaultVolume,
          DuplicityKeyPair, BitLockerVolume, etc.)
      user: models.User object of the user that retrieved the secret.
    """
    data = {
        'entity': entity,
        'helpdesk_email': settings.HELPDESK_EMAIL,
        'helpdesk_name': settings.HELPDESK_NAME,
        'retrieved_by': user.user.email(),
        }
    body = self.RenderTemplate('retrieval_email.txt', data, response_out=False)

    user_email = user.user.email()
    try:
      # If the user has access to "silently" retrieve keys without the owner
      # being notified, email only SILENT_AUDIT_ADDRESSES.
      self.VerifyPermissions(permissions.SILENT_RETRIEVE, user=user)
      to = [user_email] + settings.SILENT_AUDIT_ADDRESSES
    except models.AccessDeniedError:
      # Otherwise email the owner and RETRIEVE_AUDIT_ADDRESSES.
      to = [user_email] + settings.RETRIEVE_AUDIT_ADDRESSES
      if entity.owner:
        owner_email = '%s@%s' % (entity.owner, settings.DEFAULT_EMAIL_DOMAIN)
        to.append(owner_email)

    subject_var = '%s_RETRIEVAL_EMAIL_SUBJECT' % entity.ESCROW_TYPE_NAME.upper()
    subject = getattr(
        settings, subject_var, 'Escrow secret retrieval notification.')
    util.SendEmail(to, subject, body)

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
    permission_type = permission_type or self.PERMISSION_TYPE
    if not permission_type:
      raise models.AccessDeniedError('permission_type not specified')

    if user is None:
      user = models.GetCurrentUser()

    try:
      if not user.HasPerm(required_permission, permission_type=permission_type):
        raise models.AccessDeniedError(
            'User lacks %s permission' % required_permission)
    except ValueError:
      raise models.AccessDeniedError(
          'unknown permission_type: %s' % permission_type)

    return user

  def VerifyAllPermissionTypes(self, required_permission, user=None):
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
        user = self.VerifyPermissions(
            required_permission, user=user, permission_type=permission_type)
        perms[permission_type] = True
      except models.AccessDeniedError:
        perms[permission_type] = False
    # TODO(user): if use of this method widens, consider returning a
    #    collections.namedtuple instead of a basic dict.
    return perms

  def VerifyEscrow(self, volume_uuid):
    """Handles a GET to verify if a volume uuid has an escrowed secret."""
    self.VerifyPermissions(permissions.ESCROW)
    entity = self.SECRET_MODEL.get_by_key_name(volume_uuid)
    if not entity:
      self.error(404)
    else:
      self.response.out.write('Escrow verified.')

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
    if issubclass(exception.__class__, models.AccessError):
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
