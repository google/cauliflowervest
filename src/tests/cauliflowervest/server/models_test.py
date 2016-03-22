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
#
#

"""models module tests."""



import datetime
import os


import mock
import tests.appenginesdk

from google.appengine.api import users
from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import db
from google.appengine.ext import testbed

from google.apputils import app
from google.apputils import basetest

from cauliflowervest import settings as base_settings
from cauliflowervest.server import models
from cauliflowervest.server import settings


class BaseModelTest(basetest.TestCase):
  """Base class for testing App Engine Datastore models."""

  def setUp(self):
    self.user_email = 'user@example.com'
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.setup_env(user_email=self.user_email, overwrite=True)

    policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
    self.testbed.init_datastore_v3_stub(consistency_policy=policy)

    self.testbed.init_user_stub()
    # Ensure we use KEY_TYPE_DATASTORE_FILEVAULT and KEY_TYPE_DATASTORE_XSRF for
    # tests.
    self.key_type_default_filevault_save = settings.KEY_TYPE_DEFAULT_FILEVAULT
    self.key_type_default_xsrf_save = settings.KEY_TYPE_DEFAULT_XSRF
    settings.KEY_TYPE_DEFAULT_FILEVAULT = settings.KEY_TYPE_DATASTORE_FILEVAULT
    settings.KEY_TYPE_DEFAULT_XSRF = settings.KEY_TYPE_DATASTORE_XSRF

  def tearDown(self):
    self.testbed.deactivate()
    settings.KEY_TYPE_DEFAULT_FILEVAULT = self.key_type_default_filevault_save
    settings.KEY_TYPE_DEFAULT_XSRF = self.key_type_default_xsrf_save

  def testAutoUpdatingUserProperty(self):
    class FooModel(models.db.Model):
      user = models.AutoUpdatingUserProperty()

    appengine_user = models.users.get_current_user()

    # Test setting the property and ensuring the set value is returned.
    e = FooModel()
    e.user = appengine_user
    self.assertEqual(e.user, appengine_user)

    # Leave the property unset, and test GetCurrentUser is called.
    e = FooModel()
    self.assertEqual(e.user, appengine_user)


class GetCurrentUserTest(basetest.TestCase):

  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_all_stubs()

  def tearDown(self):
    self.testbed.deactivate()

  def testGetCurrentUser(self):
    self.testbed.setup_env(user_email='stub1@example.com', overwrite=True)

    user = models.GetCurrentUser()

    self.assertEqual('stub1@example.com', user.user.email())
    self.assertEqual(0, len(user.bitlocker_perms))
    self.assertEqual(0, len(user.duplicity_perms))
    self.assertEqual(0, len(user.filevault_perms))
    self.assertEqual(0, len(user.luks_perms))

  def testGetCurrentUserWhenNewAdmin(self):
    self.testbed.setup_env(
        user_email='stub2@example.com', user_is_admin='1', overwrite=True)

    user = models.GetCurrentUser()

    self.assertEqual('stub2@example.com', user.user.email())
    self.assertNotEqual(0, len(user.bitlocker_perms))
    self.assertNotEqual(0, len(user.duplicity_perms))
    self.assertNotEqual(0, len(user.filevault_perms))
    self.assertNotEqual(0, len(user.luks_perms))



class FileVaultVolumeTest(BaseModelTest):
  """Tests FileVaultVolume class."""

  def setUp(self):
    super(FileVaultVolumeTest, self).setUp()
    self.fvv_data = {
        'hdd_serial': 'XX123456',
        'platform_uuid': 'A4E75A65-FC39-441C-BEF5-49D9A3DC6BE0',
        'serial': 'XX123456',
        'passphrase': 'SECRET',
        'volume_uuid': '4E6A59FF-3D85-4B1C-A5D5-70F8B8A9B4A0',
        'created_by': users.User('test@example.com'),
    }
    self.fvv = models.FileVaultVolume(**self.fvv_data)

  def testSecretProperty(self):
    self.assertEqual(self.fvv.secret, 'SECRET')

  def testSecretChecksum(self):
    self.assertEqual(
        self.fvv.checksum, models.hashlib.md5('SECRET').hexdigest())

  def testPutWithoutKeyName(self):
    fvv = models.FileVaultVolume()
    self.assertRaises(models.FileVaultAccessError, fvv.put)

  def testPutWithOnlyCreatedModified(self):
    self.fvv.put()
    self.fvv.created = datetime.datetime.now()
    self.assertRaises(models.FileVaultAccessError, self.fvv.put)

  def testPutWithExistingDataModified(self):
    self.fvv.put()
    num_of_modifications = 1
    for name, prop in self.fvv.properties().iteritems():
      old_value = getattr(self.fvv, name)
      if isinstance(prop, db.DateTimeProperty):
        continue
      elif isinstance(prop, db.BooleanProperty):
        new_value = not bool(old_value)
      elif isinstance(prop, db.UserProperty):
        new_value = users.User('junk@example.com')
      else:
        new_value = 'JUNK'

      fvv = models.FileVaultVolume(**self.fvv_data)

      setattr(fvv, name, new_value)
      fvv.put()
      num_of_modifications += 1

      volumes = models.FileVaultVolume.all().fetch(999)
      self.assertEqual(num_of_modifications, len(volumes))

  def testPutWithExistingOwnerModified(self):
    self.fvv.put()
    fvv = models.FileVaultVolume(**self.fvv_data)
    fvv.owner = 'new_owner1'
    fvv.put()
    fvv = models.FileVaultVolume(**self.fvv_data)
    fvv.owner = 'new_owner2'
    fvv.put()

  def testPutWithEmptyRequiredProperty(self):
    key_name = u'foo'
    fvv = models.FileVaultVolume(key_name=key_name)

    self.assertRaises(models.FileVaultAccessError, fvv.put)

  def testPutSuccess(self):
    fvv = models.FileVaultVolume()
    for p in models.FileVaultVolume.REQUIRED_PROPERTIES:
      setattr(fvv, p, 'something')

    fvv.put()


class NormalizeHostnameTest(BaseModelTest):
  """Tests the NormalizeHostname classmethod for all escrow types."""

  def testBaseVolume(self):
    self.assertEqual('foohost', models.BaseVolume.NormalizeHostname('FOOHOST'))
    self.assertEqual(
        'foohost', models.BaseVolume.NormalizeHostname(
            'Foohost.domain.com', strip_fqdn=True))

  def testBitLockerVolume(self):
    self.assertEqual(
        'FOOHOST', models.BitLockerVolume.NormalizeHostname('foohost.dom.com'))

  def testDuplicityKeyPair(self):
    self.assertEqual(
        'foohost.dom.com',
        models.DuplicityKeyPair.NormalizeHostname('FOOHOST.dom.com'))

  def testFileVaultVolume(self):
    self.assertEqual(
        'foohost', models.FileVaultVolume.NormalizeHostname('FOOHOST.dom.com'))

  def testLuksVolume(self):
    self.assertEqual(
        'foohost.dom.com',
        models.LuksVolume.NormalizeHostname('FOOHOST.dom.com'))


class UserTest(BaseModelTest):
  """Tests User class."""

  def testHasPermBitLocker(self):
    user = models.User()
    user.bitlocker_perms = list(models.permissions.SET_REGULAR)
    self.assertTrue(user.HasPerm(
        models.permissions.SEARCH, models.permissions.TYPE_BITLOCKER))

  def testHasPermFileVault(self):
    user = models.User()
    user.filevault_perms = list(models.permissions.SET_REGULAR)
    self.assertTrue(user.HasPerm(
        models.permissions.SEARCH, models.permissions.TYPE_FILEVAULT))

  def testHasPermWithUnknownPermissionType(self):
    user = models.User()
    self.assertRaises(
        ValueError, user.HasPerm, models.permissions.SEARCH, 'NOT VALID')

  def testSetPermsBitLocker(self):
    user = models.User()
    user.SetPerms(
        models.permissions.SET_REGULAR, models.permissions.TYPE_BITLOCKER)
    self.assertTrue(user.HasPerm(
        models.permissions.SEARCH, models.permissions.TYPE_BITLOCKER))

  def testSetPermsFileVault(self):
    user = models.User()
    user.SetPerms(
        models.permissions.SET_REGULAR, models.permissions.TYPE_FILEVAULT)
    self.assertTrue(user.HasPerm(
        models.permissions.RETRIEVE, models.permissions.TYPE_FILEVAULT))

  def testSetPermsWithUnknownPermissionType(self):
    user = models.User()
    self.assertRaises(
        ValueError, user.SetPerms, [models.permissions.SEARCH], 'NOT VALID')


class AccessLogTest(BaseModelTest):
  """Tests AccessLog class."""

  @mock.patch.object(models, 'GetCurrentUser')
  @mock.patch.object(models.memcache, 'incr')
  def testPut(self, incr, get_current_user):
    incr.return_value = 1
    get_current_user.side_effect = models.AccessDeniedError('no user')

    log = models.AccessLog()
    log.put()

    incr.assert_called_once_with('AccessLogCounter', initial_value=0)


def main(unused_argv):
  basetest.main()


if __name__ == '__main__':
  app.run()
