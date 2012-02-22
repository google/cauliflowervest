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

from cauliflowervest.server import models
from cauliflowervest.server import settings


class FileVaultAccessHandler(object):
  """Class which handles FileVaultAccessError exceptions."""

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
      models.FileVaultAccessDeniedError: the user was unknown or not a member of
          the expected domain.
    """
    user = models.GetCurrentUser()
    if not user:
      raise models.FileVaultAccessDeniedError('User is unknown.', self.request)
    elif not user.email().endswith('@%s' % settings.AUTH_DOMAIN):
      raise models.FileVaultAccessDeniedError(
          'User (%s) is not a member of the expected domain (%s)' % (
              user.email(), settings.AUTH_DOMAIN),
          self.request)
    return user

  def VerifyPermissions(self, required_permission, user=None):
    """Verifies a valid user is logged in.

    Args:
      required_permission: permission string from permissions.*.
      user: optional, models.User entity; default current user.
    Returns:
      models.User object of the current user.
    Raises:
      models.FileVaultAccessDeniedError: there was a permissions issue.
    """
    if user is None:
      user = models.GetCurrentUser(get_model_user=True)
    if not user:
      raise models.FileVaultAccessDeniedError('Unknown user', self.request)
    elif not user.HasPerm(required_permission):
      raise models.FileVaultAccessDeniedError(
          'User lacks %s permission' % required_permission, self.request)
    return user

  # pylint: disable-msg=C6409
  def handle_exception(self, exception, debug_mode):
    """Handle an exception.

    Args:
      exception: exception that was thrown
      debug_mode: True if the application is running in debug mode
    """
    if issubclass(exception.__class__, models.FileVaultAccessError):
      models.FileVaultAccessLog.Log(
          successful=False, message=exception.message,
          request=exception.request)

      exc_type, exc_value, exc_tb = sys.exc_info()
      tb = traceback.format_exception(exc_type, exc_value, exc_tb)
      logging.warning('handle_exception: %s', ''.join(tb))

      self.error(exception.error_code)
      if issubclass(exception.__class__, models.FileVaultAccessDeniedError):
        self.response.out.write('Access denied.')
      else:
        self.response.out.write(cgi.escape(exception.message))
    else:
      super(FileVaultAccessHandler, self).handle_exception(
          exception, debug_mode)
