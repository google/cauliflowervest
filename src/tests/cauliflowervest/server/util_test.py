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
"""util module tests."""


import mock

import tests.appenginesdk
from google.apputils import app
from google.apputils import basetest
from cauliflowervest.server import util
from tests.cauliflowervest.server.handlers import test_util


class SendEmailTest(basetest.TestCase):
  """Test the util module."""

  def setUp(self):
    super(SendEmailTest, self).setUp()
    test_util.SetUpTestbedTestCase(self)

  def tearDown(self):
    super(SendEmailTest, self).tearDown()
    test_util.SetUpTestbedTestCase(self)

  @mock.patch.dict(util.settings.__dict__, {'DEVELOPMENT': False})
  def testOk(self):
    recipients = ['foo1@example.com', 'foo2@example.com']
    reply_to = 'replyhere@example.com'
    sender = 'sender@example.com'
    subject = 'This is only a test!'
    body = 'Only a unit test.\nReally.\nNothing to see here.'
    bcc_recipients = ['bcc1@example.com']

    util.SendEmail(
        recipients, subject, body, sender=sender, reply_to=reply_to,
        bcc_recipients=bcc_recipients, defer=False)

    mail_stub = self.testbed.get_stub('mail')
    self.assertEqual(1, len(mail_stub.get_sent_messages()))

  @mock.patch.dict(util.settings.__dict__, {'DEVELOPMENT': False})
  def testWithDefaults(self):
    recipients = ['foo1@example.com', 'foo2@example.com']
    subject = 'This is only a test!'
    body = 'Only a unit test.\nReally.\nNothing to see here.'

    util.SendEmail(recipients, subject, body, defer=False)

    mail_stub = self.testbed.get_stub('mail')
    messages = mail_stub.get_sent_messages()
    self.assertEqual(1, len(messages))
    self.assertEquals(
        messages[0].reply_to, util.settings.DEFAULT_EMAIL_REPLY_TO)

  @mock.patch.dict(util.settings.__dict__, {'DEVELOPMENT': False})
  @mock.patch.object(util.deferred, 'defer')
  def testOkDefaultIsDefer(self, defer):
    recipients = ['foo1@example.com', 'foo2@example.com']
    reply_to = 'replyhere@example.com'
    sender = 'sender@example.com'
    subject = 'This is only a test!'
    body = 'Only a unit test.\nReally.\nNothing to see here.'
    bcc = ['bcc1@example.com']

    util.SendEmail(
        recipients, subject, body, sender=sender, reply_to=reply_to,
        bcc_recipients=bcc)

    defer.assert_called_once_with(
        util._Send, recipients, subject, body, sender, reply_to, bcc)

  @mock.patch.dict(util.settings.__dict__, {'DEFAULT_EMAIL_SENDER': ''})
  def testSendWithInvalidSender(self):
    util._Send(
        ['foo@example.com'], 'subject', 'body', '', '', '')

    mail_stub = self.testbed.get_stub('mail')
    self.assertEqual(0, len(mail_stub.get_sent_messages()))


class XsrfTest(basetest.TestCase):

  def setUp(self):
    util.crypto.ENCRYPTION_KEY_TYPES[
        util.settings.KEY_TYPE_DEFAULT_XSRF] = lambda: 'seekrit'

  def testXsrf(self):
    timestamp1 = 1329858903.8305809
    timestamp2 = 1329859175.3705659
    token1 = 'fZDmmR1yZzyjL9cyX0Zl7XwjfDEzMjk4NTg5MDMuODM='.decode('utf-8')
    token2 = util.XsrfTokenGenerate(
        'action', user='user', timestamp=timestamp1).decode('utf-8')
    token3 = util.XsrfTokenGenerate('action', user='user').decode('utf-8')
    token4 = util.XsrfTokenGenerate('action', user='user2').decode('utf-8')

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
