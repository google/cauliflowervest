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

"""CauliflowerVest email module."""




import logging

from google.appengine.api import mail

from cauliflowervest.server import settings


def SendEmail(recipients, subject, body, sender=None, reply_to=None,
              bcc_recipients=None):
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
  """
  if settings.DEVELOPMENT:
    logging.warn('Not sending email in development mode')
    logging.info(
        'Would have sent email to %s:\nSubject: %s\nBody:\n\n%s',
        recipients, subject, body)
  else:
    message = mail.EmailMessage(
        to=recipients,
        reply_to=reply_to or settings.DEFAULT_EMAIL_REPLY_TO,
        sender=sender or settings.DEFAULT_EMAIL_SENDER,
        subject=subject,
        body=body)
    if bcc_recipients:
      message.bcc_recipients = bcc_recipients
    message.send()