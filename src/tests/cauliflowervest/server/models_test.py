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

"""models module tests."""



import mox
import stubout
import tests.appenginesdk

from google.appengine.ext import testbed

from google.apputils import app
from google.apputils import basetest

from cauliflowervest.server import models


class BaseModelTest(mox.MoxTestBase):
  """Base class for testing App Engine Datastore models."""

  def setUp(self):
    mox.MoxTestBase.setUp(self)
    self.stubs = stubout.StubOutForTesting()
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()

  def tearDown(self):
    self.mox.UnsetStubs()
    self.stubs.UnsetAll()


class GetCurrentUserTest(mox.MoxTestBase):
  def setUp(self):
    mox.MoxTestBase.setUp(self)
    self.stubs = stubout.StubOutForTesting()

  def tearDown(self):
    self.mox.UnsetStubs()
    self.stubs.UnsetAll()

  def testGaia(self):
    self.mox.StubOutWithMock(models.users, 'get_current_user')

    models.users.get_current_user().AndReturn('user')

    self.mox.ReplayAll()
    self.assertEqual('user', models.GetCurrentUser())
    self.mox.VerifyAll()

  def testGetModelUser(self):
    self.mox.StubOutWithMock(models.users, 'get_current_user')
    self.mox.StubOutWithMock(models.User, 'get_by_key_name')

    mock_user = self.mox.CreateMockAnything()
    mock_user_entity = self.mox.CreateMockAnything()

    models.users.get_current_user().AndReturn(mock_user)
    mock_user.email().AndReturn('user@example.com')
    models.User.get_by_key_name(
        'user@example.com').AndReturn(mock_user_entity)

    self.mox.ReplayAll()
    self.assertEqual(
        mock_user_entity, models.GetCurrentUser(get_model_user=True))
    self.mox.VerifyAll()

  def testGetModelUserWhenNewAdmin(self):
    self.mox.StubOutWithMock(models.users, 'get_current_user')
    self.mox.StubOutWithMock(models.User, 'get_by_key_name')
    self.mox.StubOutWithMock(models.users, 'is_current_user_admin')
    self.mox.StubOutWithMock(models, 'User')

    email = 'user@example.com'

    mock_user = self.mox.CreateMockAnything()
    mock_user_entity = self.mox.CreateMockAnything()

    models.users.get_current_user().AndReturn(mock_user)
    mock_user.email().AndReturn(email)
    models.User.get_by_key_name(email).AndReturn(None)
    models.users.is_current_user_admin().AndReturn(True)
    mock_user.email().AndReturn(email)
    models.User(key_name=email).AndReturn(mock_user_entity)
    mock_user.email().AndReturn(email)
    mock_user_entity.put().AndReturn(None)

    self.mox.ReplayAll()
    self.assertEqual(
        mock_user_entity, models.GetCurrentUser(get_model_user=True))
    self.mox.VerifyAll()



class FileVaultVolumeTest(BaseModelTest):
  """Tests FileVaultVolume class."""

  def testPutWithoutKeyName(self):
    fvv = models.FileVaultVolume()
    self.assertRaises(models.FileVaultAccessError, fvv.put)

  def testPutWithExistingKeyName(self):
    self.mox.StubOutWithMock(models.FileVaultVolume, 'get_by_key_name')
    key_name = u'foo'
    fvv = models.FileVaultVolume(key_name=key_name)
    models.FileVaultVolume.get_by_key_name(key_name).AndReturn('yes!')

    self.mox.ReplayAll()
    self.assertRaises(models.FileVaultAccessError, fvv.put)
    self.mox.VerifyAll()

  def testPutWithEmptyRequiredProperty(self):
    self.mox.StubOutWithMock(models.FileVaultVolume, 'get_by_key_name')
    key_name = u'foo'
    fvv = models.FileVaultVolume(key_name=key_name)
    models.FileVaultVolume.get_by_key_name(key_name).AndReturn(None)

    self.mox.ReplayAll()
    self.assertRaises(models.FileVaultAccessError, fvv.put)
    self.mox.VerifyAll()

  def testPutSuccess(self):
    self.mox.StubOutWithMock(models.db.Model, 'put')
    self.mox.StubOutWithMock(models.FileVaultVolume, 'get_by_key_name')
    key_name = u'foo'
    fvv = models.FileVaultVolume(key_name=key_name)
    models.FileVaultVolume.get_by_key_name(key_name).AndReturn(None)
    for p in models.FileVaultVolume.REQUIRED_PROPERTIES:
      setattr(fvv, p, 'something')
    models.db.Model.put().AndReturn(None)

    self.mox.ReplayAll()
    fvv.put()
    self.mox.VerifyAll()


def main(unused_argv):
  basetest.main()


if __name__ == '__main__':
  app.run()