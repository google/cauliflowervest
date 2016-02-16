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

"""filevault module tests."""



import mock

from django.conf import settings
settings.configure()

from google.appengine.api import users

from google.apputils import app
from google.apputils import basetest

from cauliflowervest.server import handlers
from cauliflowervest.server import main as gae_main
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server.handlers import filevault as fv
from tests.cauliflowervest.server.handlers import test_util


class FileVaultAccessHandlerTest(basetest.TestCase):
  """Test the filevault.FileVault class."""

  def setUp(self):
    super(FileVaultAccessHandlerTest, self).setUp()

    test_util.SetUpTestbedTestCase(self)

    self.c = fv.FileVault()

  def tearDown(self):
    super(FileVaultAccessHandlerTest, self).tearDown()
    test_util.TearDownTestbedTestCase(self)

  def testCreateNewSecretEntity(self):
    result = self.c._CreateNewSecretEntity(
        'mock_owner', 'mock_volume_uuid', 'mock_secret')
    self.assertIsInstance(result, fv.models.FileVaultVolume)

  def testIsValidSecret(self):
    self.assertTrue(
        self.c.IsValidSecret('AD8C7732-6447-4EA9-B312-B438050C4988'))
    self.assertFalse(self.c.IsValidSecret('xyz'))


class FileVaultChangeOwnerAccessHandlerTest(basetest.TestCase):
  """Test the filevault.FileVaultChangeOwner class."""

  def setUp(self):
    super(FileVaultChangeOwnerAccessHandlerTest, self).setUp()

    settings.KEY_TYPE_DEFAULT_FILEVAULT = settings.KEY_TYPE_DATASTORE_FILEVAULT
    settings.KEY_TYPE_DEFAULT_XSRF = settings.KEY_TYPE_DATASTORE_XSRF

    test_util.SetUpTestbedTestCase(self)

    self.volume_uuid = '4E6A59FF-3D85-4B1C-A5D5-70F8B8A9B4A0'
    self.change_owner_url = '/filevault/%s/change-owner' % self.volume_uuid

    self.user = models.User(
        key_name='stub7@example.com', user=users.User('stub7@example.com'))
    self.user.filevault_perms = [permissions.CHANGE_OWNER]
    self.user.put()

    fvv = models.FileVaultVolume(
        key_name=self.volume_uuid,
        hdd_serial='XX123456',
        platform_uuid='A4E75A65-FC39-441C-BEF5-49D9A3DC6BE0',
        serial='XX123456',
        passphrase='SECRET',
        volume_uuid=self.volume_uuid,
        created_by=users.User('stub7@example.com'))
    fvv.put()

  def tearDown(self):
    super(FileVaultChangeOwnerAccessHandlerTest, self).tearDown()
    test_util.TearDownTestbedTestCase(self)

  def testChangeOwner(self):
    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      resp = gae_main.app.get_response(
          self.change_owner_url,
          {'REQUEST_METHOD': 'POST'},
          POST={'new_owner': 'mew'})
    self.assertEqual(200, resp.status_int)
    self.assertEqual('mew', models.FileVaultVolume.get_by_key_name(
        self.volume_uuid).owner)

  def testChangeOwnerForNonexistantUuid(self):
    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      resp = gae_main.app.get_response(
          '/filevault/%s/change-owner' % 'junk-uuid',
          {'REQUEST_METHOD': 'POST'},
          POST={'new_owner': 'mew'})
    self.assertEqual(404, resp.status_int)

  def testChangeOwnerWithoutValidXsrf(self):
    resp = gae_main.app.get_response(
        self.change_owner_url,
        {'REQUEST_METHOD': 'POST'},
        POST={'new_owner': 'mew'})
    self.assertEqual(403, resp.status_int)

  def testChangeOwnerWithoutPermission(self):
    self.user.filevault_perms = []
    self.user.put()
    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      resp = gae_main.app.get_response(
          self.change_owner_url,
          {'REQUEST_METHOD': 'POST'},
          POST={'new_owner': 'mew'})
    self.assertEqual(403, resp.status_int)


def main(_):
  basetest.main()


if __name__ == '__main__':
  app.run()
