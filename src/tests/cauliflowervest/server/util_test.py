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
        bcc_recipients=bcc_recipients, defer=False)
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
    util.SendEmail(recipients, subject, body, defer=False)
    util.settings.DEVELOPMENT = orig_dev
    self.mox.VerifyAll()

  def testOkDefaultIsDefer(self):
    self.mox.StubOutWithMock(util.deferred, 'defer', True)

    recipients = ['foo1@example.com', 'foo2@example.com']
    reply_to = 'replyhere@example.com'
    sender = 'sender@example.com'
    subject = 'This is only a test!'
    body = 'Only a unit test.\nReally.\nNothing to see here.'
    bcc_recipients = ['bcc1@example.com']

    util.deferred.defer(
        util._Send, recipients, subject, body, sender, reply_to,
        bcc_recipients).AndReturn(None)

    self.mox.ReplayAll()
    orig_dev = util.settings.DEVELOPMENT
    util.settings.DEVELOPMENT = False
    util.SendEmail(
        recipients, subject, body, sender=sender, reply_to=reply_to,
        bcc_recipients=bcc_recipients)
    util.settings.DEVELOPMENT = orig_dev
    self.mox.VerifyAll()


class XsrfTest(mox.MoxTestBase):
  def setUp(self):
    mox.MoxTestBase.setUp(self)
    self.stubs = stubout.StubOutForTesting()

    util.crypto.ENCRYPTION_KEY_TYPES[
        util.settings.KEY_TYPE_DEFAULT_XSRF] = lambda: 'seekrit'

  def tearDown(self):
    self.mox.UnsetStubs()
    self.stubs.UnsetAll()

  def testXsrf(self):
    timestamp1 = 1329858903.8305809
    timestamp2 = 1329859175.3705659
    token1 = 'fZDmmR1yZzyjL9cyX0Zl7XwjfDEzMjk4NTg5MDMuODM='
    token2 = util.XsrfTokenGenerate('action', user='user', timestamp=timestamp1)
    token3 = util.XsrfTokenGenerate('action', user='user')
    token4 = util.XsrfTokenGenerate('action', user='user2')

    self.assertEquals(token1, token2)
    self.assertNotEquals(token1, token3)
    self.assertNotEquals(token3, token4)

    class MockTime1(object):
      def time(self):  # pylint: disable=g-bad-name
        return timestamp1

    class MockTime2(object):
      def time(self):  # pylint: disable=g-bad-name
        return timestamp1 + 999

    self.assertTrue(util.XsrfTokenValidate(
        token1, 'action', user='user', time_=MockTime1()))
    self.assertFalse(util.XsrfTokenValidate(
        token1, 'action', user='user', time_=MockTime2()))
    self.assertTrue(util.XsrfTokenValidate(
        token1, 'action', user='user', timestamp=timestamp1, time_=MockTime1()))
    self.assertFalse(util.XsrfTokenValidate(
        token1, 'action', user='user', timestamp=timestamp2, time_=MockTime1()))


def main(unused_argv):
  basetest.main()


if __name__ == '__main__':
  app.run()