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

"""Base class for all handlers."""
import cgi
import logging
import sys
import traceback

import webapp2

from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.models import base
from cauliflowervest.server.models import errors




def VerifyPermissions(required_permission, user, permission_type):
  """Verifies a valid user is logged in.

  Args:
    required_permission: permission string from permissions.*.
    user: base.User entity; default current user.
    permission_type: string, one of permission.TYPE_* variables.
  Raises:
    errors.AccessDeniedError: there was a permissions issue.
  """
  if not permission_type:
    raise errors.AccessDeniedError('permission_type not specified')

  try:
    if not user.HasPerm(required_permission, permission_type=permission_type):
      raise errors.AccessDeniedError(
          'User lacks %s permission' % required_permission)
  except ValueError:
    raise errors.AccessDeniedError(
        'unknown permission_type: %s' % permission_type)


def VerifyAllPermissionTypes(required_permission, user=None):
  """Verifies if a user has the required_permission for all permission types.

  Args:
    required_permission: permission string from permissions.*.
    user: optional, base.User entity; default current user.
  Returns:
    Dict. Keys are permissions.TYPES values, and value booleans, True when
    the user has the required_permission for the permission type, False
    otherwise.
  """
  if user is None:
    user = base.GetCurrentUser()

  perms = {}
  for permission_type in permissions.TYPES:
    try:
      VerifyPermissions(required_permission, user, permission_type)
      perms[permission_type] = True
    except errors.AccessDeniedError:
      perms[permission_type] = False
  #  if use of this method widens, consider returning a
  #    collections.namedtuple instead of a basic dict.
  return perms


class BaseHandler(webapp2.RequestHandler):
  """Class which handles AccessError exceptions."""

  AUDIT_LOG_MODEL = base.AccessLog

  def VerifyXsrfToken(self, action, email=None):
    """Verifies a valid XSRF token was passed for the current request.

    Args:
      action: String, validate the token against this action.
      email: optional, str; current user's email.
    Returns:
      Boolean. True if the XSRF Token was valid.
    Raises:
      errors.AccessDeniedError: the XSRF token was invalid or not supplied.
    """
    xsrf_token = self.request.get('xsrf-token', None)
    if settings.XSRF_PROTECTION_ENABLED:
      if not util.XsrfTokenValidate(xsrf_token, action, user=email):
        raise errors.AccessDeniedError('Valid XSRF token not provided')
    elif not xsrf_token:
      logging.info(
          'Ignoring missing XSRF token; settings.XSRF_PROTECTION_ENABLED=False')
    return True

  def handle_exception(self, exception, debug_mode):
    """Handle an exception.

    Args:
      exception: exception that was thrown
      debug_mode: True if the application is running in debug mode
    """
    if issubclass(exception.__class__, errors.Error):
      self.AUDIT_LOG_MODEL.Log(
          successful=False, message=exception.message, request=self.request)

      exc_type, exc_value, exc_tb = sys.exc_info()
      tb = traceback.format_exception(exc_type, exc_value, exc_tb)
      logging.warning('handle_exception: %s', ''.join(tb))

      self.error(exception.error_code)
      if issubclass(exception.__class__, errors.AccessDeniedError):
        self.response.out.write('Access denied.')
      else:
        self.response.out.write(cgi.escape(exception.message))
    else:
      super(BaseHandler, self).handle_exception(exception, debug_mode)
