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

"""models module tests."""

import os



from absl.testing import absltest
import mock

from google.appengine.ext import db

from cauliflowervest import settings as base_settings
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import base
from cauliflowervest.server.models import errors


class GetCurrentUserTest(test_util.BaseTest):

  def testAutoUpdatingUserProperty(self):
    class FooModel(db.Model):
      user = base.AutoUpdatingUserProperty()

    appengine_user = base.users.get_current_user()

    # Test setting the property and ensuring the set value is returned.
    e = FooModel()
    e.user = appengine_user
    self.assertEqual(e.user, appengine_user)

    # Leave the property unset, and test GetCurrentUser is called.
    e = FooModel()
    self.assertEqual(e.user, appengine_user)

  def testGetCurrentUser(self):
    self.testbed.setup_env(user_email='stub1@example.com', overwrite=True)

    user = base.GetCurrentUser()

    self.assertEqual('stub1@example.com', user.user.email())
    self.assertEqual(0, len(user.bitlocker_perms))
    self.assertEqual(0, len(user.duplicity_perms))
    self.assertEqual(0, len(user.filevault_perms))
    self.assertEqual(0, len(user.luks_perms))

  def testGetCurrentUserWhenNewAdmin(self):
    self.testbed.setup_env(
        user_email='stub2@example.com', user_is_admin='1', overwrite=True)

    user = base.GetCurrentUser()

    self.assertEqual('stub2@example.com', user.user.email())
    self.assertNotEqual(0, len(user.bitlocker_perms))
    self.assertNotEqual(0, len(user.duplicity_perms))
    self.assertNotEqual(0, len(user.filevault_perms))
    self.assertNotEqual(0, len(user.luks_perms))

  def testWithInvalidOauthId(self):
    self.testbed.setup_env(
        user_email='', oauth_email='zaspire@example.com',
        oauth_auth_domain='example.com', oauth_user_id='1', overwrite=True)
    self.assertRaises(errors.AccessDeniedError, base.GetCurrentUser)



class NormalizeHostnameTest(test_util.BaseTest):
  """Tests the NormalizeHostname classmethod for all escrow types."""

  def testBasePassphrase(self):
    self.assertEqual(
        'foohost', base.BasePassphrase.NormalizeHostname('FOOHOST'))
    self.assertEqual(
        'foohost', base.BasePassphrase.NormalizeHostname(
            'Foohost.domain.com', strip_fqdn=True))


class AccessLogTest(test_util.BaseTest):
  """Tests AccessLog class."""

  @mock.patch.object(base, 'GetCurrentUser')
  @mock.patch.object(base.memcache, 'incr')
  def testPut(self, incr, get_current_user):
    incr.return_value = 1
    get_current_user.side_effect = errors.AccessDeniedError('no user')

    log = base.AccessLog()
    log.put()

    incr.assert_called_once_with('AccessLogCounter', initial_value=0)


class OwnerPropertyTest(test_util.BaseTest):

  def testNormalize(self):
    p = base.BasePassphrase(owner='zerocool')
    self.assertEqual('zerocool@example.com', p.owner)

  def testMultiOwner(self):
    p = base.BasePassphrase(owner='zerocool')
    self.assertEqual(['zerocool@example.com'], p.owners)


if __name__ == '__main__':
  absltest.main()
