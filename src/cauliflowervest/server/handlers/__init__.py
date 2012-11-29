#!/usr/bin/env python
#
# Copyright 2011 Google Inc. All Rights Reserved.

"""Top level __init__ for handlers package."""


import cgi
import Cookie
import logging
import os
import re
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


class AccessHandler(webapp2.RequestHandler):
  """Class which handles AccessError exceptions."""

  AUDIT_LOG_MODEL = None
  PERMISSION_TYPE = None

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
    html = template.render(os.path.join(TEMPLATE_DIR, template_path), params)
    if response_out:
      self.response.out.write(html)
    else:
      return html

  def SanitizeString(self, s):
    """Returns a sanitized string with html escaped."""
    return cgi.escape(s)

  def IsSaneUuid(self, uuid):
    """Returns true if uuid str is a sanely formatted uuid."""
    return re.search(r'^[0-9A-Z\-]+$', uuid) is not None

  def VerifyDomainUser(self):
    """Verifies the current user is of the expected domain.

    Returns:
      users.User object of the current user.
    Raises:
      models.AccessDeniedError: the user was unknown or not a member of
          the expected domain.
    """
    user = models.GetCurrentUser()
    if not user:
      raise models.AccessDeniedError('User is unknown.', self.request)
    elif not user.email().endswith('@%s' % settings.AUTH_DOMAIN):
      raise models.AccessDeniedError(
          'User (%s) is not a member of the expected domain (%s)' % (
              user.email(), settings.AUTH_DOMAIN),
          self.request)
    return user

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
      ValueError: neither permission_type nor PERMISSION_TYPE are set.
    """
    permission_type = permission_type or self.PERMISSION_TYPE
    if not permission_type:
      raise ValueError('permission_type required')

    if user is None:
      user = models.GetCurrentUser(get_model_user=True)
    if not user:
      raise models.AccessDeniedError('Unknown user', self.request)
    elif not user.HasPerm(required_permission, permission_type=permission_type):
      raise models.AccessDeniedError(
          'User lacks %s permission' % required_permission, self.request)
    return user

  def VerifyAllPermissionTypes(self, required_permission, user=None):
    """Verifies if a user has the required_permission for all permision types.

    Args:
      required_permission: permission string from permissions.*.
      user: optional, models.User entity; default current user.
    Returns:
      Dict. Keys are permissions.TYPES values, and value booleans, True when
      the user has the required_permission for the permission type, False
      otherwise.
    """
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

  def VerifyXsrfToken(self, action):
    """Verifies a valid XSRF token was passed for the current request.

    Args:
      action: String, validate the token against this action.
    Returns:
      Boolean. True if the XSRF Token was valid.
    Raises:
      models.AccessDeniedError: the XSRF token was invalid or not supplied.
    """
    # TODO(user): Remove this special case on 2012/12/01.
    if action == base_settings.GET_PASSPHRASE_ACTION:
      return True

    xsrf_token = self.request.get('xsrf-token', None)
    if settings.XSRF_PROTECTION_ENABLED:
      if not util.XsrfTokenValidate(xsrf_token, action):
        raise models.AccessDeniedError(
            'Valid XSRF token not provided', self.request)
    elif not xsrf_token:
      logging.info(
          'Ignoring missing XSRF token; settings.XSRF_PROTECTION_ENABLED=False')
    return True

  # pylint: disable-msg=C6409
  def handle_exception(self, exception, debug_mode):
    """Handle an exception.

    Args:
      exception: exception that was thrown
      debug_mode: True if the application is running in debug mode
    """
    if issubclass(exception.__class__, models.AccessError):
      self.AUDIT_LOG_MODEL.Log(
          successful=False, message=exception.message,
          request=exception.request)

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
  PERMISSION_TYPE = permissions.TYPE_BITLOCKER


class FileVaultAccessHandler(AccessHandler):
  """Class which handles File vault handler."""
  AUDIT_LOG_MODEL = models.FileVaultAccessLog
  PERMISSION_TYPE = permissions.TYPE_FILEVAULT
