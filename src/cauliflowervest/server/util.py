#!/usr/bin/env python
#
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
#
"""CauliflowerVest util module."""

import base64
import exceptions
import hmac
import httplib
import json
import logging
import os
import time


import jinja2

from google.appengine.api import mail
from google.appengine.ext import deferred

from cauliflowervest.server import crypto
from cauliflowervest.server import settings
from cauliflowervest.server.models import base

JSON_PREFIX = ")]}',\n"
XSRF_DELIMITER = '|#|'
XSRF_VALID_TIME = 300  # Seconds = 5 minutes
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
_JINJA2_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
_CRON_REQUEST_HEADER = 'X-Appengine-Cron'


def _Send(recipients, subject, body, sender, reply_to, bcc_recipients):
  """Private function to send mail message with AppEngine mail API.

  Args:
    recipients: list, str email addresses to send the email to.
    subject: str, email subject.
    body: str, email body.
    sender: str, optional, email address to send the email from; defaults to
        settings.DEFAULT_EMAIL_SENDER.
    reply_to: str, optional, email address to set the Reply-To header; defaults
        to settings.DEFAULT_EMAIL_REPLY_TO.
    bcc_recipients: list, optional, str email addresses to BCC.
  """
  try:
    message = mail.EmailMessage(
        to=recipients,
        sender=sender or settings.DEFAULT_EMAIL_SENDER,
        subject=subject,
        body=body)
    if reply_to or settings.DEFAULT_EMAIL_REPLY_TO:
      message.reply_to = reply_to or settings.DEFAULT_EMAIL_REPLY_TO
  except mail.InvalidEmailError:
    logging.warning('Email settings are incorrectly configured; skipping')
    return

  if bcc_recipients:
    message.bcc = bcc_recipients

  message.send()


def SendEmail(recipients, subject, body, sender=None, reply_to=None,
              bcc_recipients=None, defer=True):
  """Sends a mail message with the AppEngine mail API.

  Args:
    recipients: list, str email addresses to send the email to.
    subject: str, email subject.
    body: str, email body.
    sender: str, optional, email address to send the email from; defaults to
        settings.DEFAULT_EMAIL_SENDER.
    reply_to: str, optional, email address to set the Reply-To header; defaults
        to settings.DEFAULT_EMAIL_REPLY_TO.
    bcc_recipients: list, optional, str email addresses to BCC.
    defer: bool, default True, send the email in a deferred task.
  """
  if settings.DEVELOPMENT:
    logging.warning('Not sending email in development mode')
    logging.info(
        'Would have sent email to %s:\nSubject: %s\nBody:\n\n%s',
        recipients, subject, body)
  else:
    if defer:
      deferred.defer(
          _Send, recipients, subject, body, sender, reply_to, bcc_recipients)
    else:
      _Send(recipients, subject, body, sender, reply_to, bcc_recipients)


def XsrfTokenGenerate(action, user=None, timestamp=None):
  """Generate an XSRF token."""
  if not user:
    # TODO(user): drop the unused user arg, find a way to cache user.
    user = base.GetCurrentUser().email
  if not timestamp:
    timestamp = time.time()
  timestr = str(timestamp)
  secret = crypto.ENCRYPTION_KEY_TYPES[settings.KEY_TYPE_DEFAULT_XSRF]()
  h = hmac.new(secret, XSRF_DELIMITER.join((user, action, timestr)))
  return base64.urlsafe_b64encode(
      ''.join((h.digest(), XSRF_DELIMITER, timestr)))


def XsrfTokenValidate(token, action, user=None, timestamp=None, time_=time):
  """Generate an XSRF token."""
  if not token:
    return False
  if not user:
    # TODO(user): drop the unused user arg, find a way to cache user.
    user = base.GetCurrentUser().email
  if not timestamp:
    try:
      # Request objects return Unicode encoded tokens.
      token = token.encode('utf-8')

      _, timestr = base64.urlsafe_b64decode(token).split(XSRF_DELIMITER, 1)
      timestamp = float(timestr)
    except ValueError:
      logging.exception('ValueError obtaining timestamp from token: %s', token)
      return False

  if timestamp + XSRF_VALID_TIME < time_.time():
    return False
  if token != XsrfTokenGenerate(action, user, timestamp):
    return False
  return True


def ToSafeJson(obj):
  """Add prefix to prevent Cross Site Script Inclusion."""
  return JSON_PREFIX + json.dumps(obj)


def FromSafeJson(data):
  """Reverse ToSafeJson."""

  if not data.startswith(JSON_PREFIX):
    raise exceptions.ValueError

  return json.loads(data[len(JSON_PREFIX):])


def RenderTemplate(filename, params):
  """Renders a template of a given path and optionally writes to response.

  Args:
    filename: str, template file name.
    params: dictionary, key/values to send to the template.render().
  Returns:
    String rendered HTML.
  """
  template = _JINJA2_ENV.get_template(filename)
  return template.render(**params)


def CronJob(original_function):
  """Decorator for protecting cron handlers."""
  def WrappedFunction(self, *args, **kwargs):
    is_cron_user = (
        os.getenv('REMOTE_ADDR', '') == '0.1.0.1'
        and self.request.headers.get(_CRON_REQUEST_HEADER, '') == 'true')
    if not (settings.TEST or is_cron_user):
      logging.warning(
          'Request to run cron job came from non-Cron Service user.')
      self.error(httplib.FORBIDDEN)
      return
    return original_function(self, *args, **kwargs)
  return WrappedFunction
