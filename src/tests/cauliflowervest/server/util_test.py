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

"""util module tests."""



import mox
import stubout

import tests.appenginesdk
from google.apputils import app
from google.apputils import basetest
from cauliflowervest.server import util


class SendEmailTest(mox.MoxTestBase):
  """Test the util module."""

  def setUp(self):
    mox.MoxTestBase.setUp(self)
    self.stubs = stubout.StubOutForTesting()

  def tearDown(self):
    self.mox.UnsetStubs()
    self.stubs.UnsetAll()

  def testOk(self):
    self.mox.StubOutWithMock(util.mail, 'EmailMessage', True)

    recipients = ['foo1@example.com', 'foo2@example.com']
    reply_to = 'replyhere@example.com'
    sender = 'sender@example.com'
    subject = 'This is only a test!'
    body = 'Only a unit test.\nReally.\nNothing to see here.'
    bcc_recipients = ['bcc1@example.com']

    mock_email = self.mox.CreateMockAnything()
    util.mail.EmailMessage(
        to=recipients,
        reply_to=reply_to,
        sender=sender,
        subject=subject,
        body=body).AndReturn(mock_email)
    mock_email.send().AndReturn(None)

    self.mox.ReplayAll()
    orig_dev = util.settings.DEVELOPMENT
    util.settings.DEVELOPMENT = False
    util.SendEmail(
        recipients, subject, body, sender=sender, reply_to=reply_to,
        bcc_recipients=bcc_recipients)
    util.settings.DEVELOPMENT = orig_dev
    self.mox.VerifyAll()

  def testWithDefaults(self):
    self.mox.StubOutWithMock(util.mail, 'EmailMessage', True)

    recipients = ['foo1@example.com', 'foo2@example.com']
    subject = 'This is only a test!'
    body = 'Only a unit test.\nReally.\nNothing to see here.'

    mock_email = self.mox.CreateMockAnything()
    orig_dev = util.settings.DEVELOPMENT
    util.settings.DEVELOPMENT = False
    util.mail.EmailMessage(
        to=recipients,
        reply_to=util.settings.DEFAULT_EMAIL_REPLY_TO,
        sender=util.settings.DEFAULT_EMAIL_SENDER,
        subject=subject,
        body=body).AndReturn(mock_email)
    mock_email.send().AndReturn(None)

    self.mox.ReplayAll()
    orig_dev = util.settings.DEVELOPMENT
    util.settings.DEVELOPMENT = False
    util.SendEmail(recipients, subject, body)
    util.settings.DEVELOPMENT = orig_dev
    self.mox.VerifyAll()


def main(unused_argv):
  basetest.main()


if __name__ == '__main__':
  app.run()