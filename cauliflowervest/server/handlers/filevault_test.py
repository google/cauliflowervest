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

"""filevault module tests."""

import httplib



import mock

from google.appengine.api import users

from absl.testing import absltest

from cauliflowervest.server import main as gae_main
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server.handlers import filevault as fv
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import base
from cauliflowervest.server.models import volumes as models


class FileVaultAccessHandlerTest(test_util.BaseTest):
  """Test the filevault.FileVault class."""

  def setUp(self):
    super(FileVaultAccessHandlerTest, self).setUp()

    self.c = fv.FileVault()

  def testCreateNewSecretEntity(self):
    result = self.c._CreateNewSecretEntity(
        'mock_owner', 'mock_volume_uuid', 'mock_secret')
    self.assertIsInstance(result, fv.models.FileVaultVolume)

  def testIsValidSecret(self):
    self.assertTrue(
        self.c.IsValidSecret('AD8C7732-6447-4EA9-B312-B438050C4988'))
    self.assertFalse(self.c.IsValidSecret('xyz'))


class FileVaultChangeOwnerAccessHandlerTest(test_util.BaseTest):
  """Test the filevault.FileVaultChangeOwner class."""

  def setUp(self):
    super(FileVaultChangeOwnerAccessHandlerTest, self).setUp()

    settings.KEY_TYPE_DEFAULT_FILEVAULT = settings.KEY_TYPE_DATASTORE_FILEVAULT
    settings.KEY_TYPE_DEFAULT_XSRF = settings.KEY_TYPE_DATASTORE_XSRF

    self.volume_uuid = '4E6A59FF-3D85-4B1C-A5D5-70F8B8A9B4A0'

    self.user = base.User(
        key_name='stub7@example.com', user=users.User('stub7@example.com'))
    self.user.filevault_perms = [permissions.CHANGE_OWNER]
    self.user.put()

    fvv = models.FileVaultVolume(
        hdd_serial='XX123456',
        platform_uuid='A4E75A65-FC39-441C-BEF5-49D9A3DC6BE0',
        serial='XX123456',
        passphrase='SECRET',
        volume_uuid=self.volume_uuid,
        created_by=users.User('stub7@example.com'))
    volume_id = fvv.put()
    self.change_owner_url = '/api/internal/change-owner/filevault/%s/' % (
        volume_id)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testChangeOwner(self):
    resp = gae_main.app.get_response(
        self.change_owner_url,
        {'REQUEST_METHOD': 'POST'},
        POST={'new_owner': 'mew'})
    self.assertEqual(httplib.OK, resp.status_int)
    self.assertEqual(
        'mew@example.com', models.FileVaultVolume.GetLatestForTarget(
            self.volume_uuid).owner)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testChangeOwnerForNonexistantUuid(self):
    resp = gae_main.app.get_response(
        '/filevault/%s/change-owner' % 'junk-uuid',
        {'REQUEST_METHOD': 'POST'},
        POST={'new_owner': 'mew'})
    self.assertEqual(httplib.NOT_FOUND, resp.status_int)

  def testChangeOwnerWithoutValidXsrf(self):
    resp = gae_main.app.get_response(
        self.change_owner_url,
        {'REQUEST_METHOD': 'POST'},
        POST={'new_owner': 'mew'})
    self.assertEqual(httplib.FORBIDDEN, resp.status_int)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testChangeOwnerWithoutPermission(self):
    self.user.filevault_perms = []
    self.user.put()
    resp = gae_main.app.get_response(
        self.change_owner_url,
        {'REQUEST_METHOD': 'POST'},
        POST={'new_owner': 'mew'})
    self.assertEqual(httplib.FORBIDDEN, resp.status_int)


if __name__ == '__main__':
  absltest.main()
