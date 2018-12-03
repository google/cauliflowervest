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

import httplib

from absl.testing import absltest
import mock
import webtest

from google.appengine.api import users
from google.appengine.ext import db

from cauliflowervest import settings as base_settings
from cauliflowervest.server import crypto
from cauliflowervest.server import main as gae_main
from cauliflowervest.server import permissions
from cauliflowervest.server import service_factory
from cauliflowervest.server import services
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import base
from cauliflowervest.server.models import firmware


class AppleFirmwareHandlerTest(test_util.BaseTest):

  def setUp(self):
    super(AppleFirmwareHandlerTest, self).setUp()

    self.testapp = webtest.TestApp(gae_main.app)
    inventory = service_factory.GetInventoryService()
    inventory.GetAssetTagsFromUploadRequest = mock.Mock(return_value=['111'])
    inventory.GetMetadataUpdates = mock.Mock(return_value={})

  def tearDown(self):
    service_factory.inventory_service = None
    super(AppleFirmwareHandlerTest, self).tearDown()

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testUpload(self):
    password = 'S3cR3t6789'
    hostname = 'host1'
    serial = 'SERIAL'
    self.testapp.put(
        '/apple_firmware/?volume_uuid=%s&hostname=%s&platform_uuid=ID1' % (
            serial, hostname),
        params=password, status=httplib.OK)

    passwords = firmware.AppleFirmwarePassword.all().fetch(None)

    self.assertEqual(1, len(passwords))
    self.assertEqual(password, passwords[0].password)
    self.assertEqual(serial, passwords[0].target_id)
    self.assertEqual(hostname, passwords[0].hostname)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testRetrieval(self):
    password = 'S3cR3t6789'
    hostname = 'host1'
    serial = 'SERIAL'
    firmware.AppleFirmwarePassword(
        serial=serial, hostname=hostname, password=password, owners=['stub7'],
        platform_uuid='ID1',
    ).put()

    resp = util.FromSafeJson(
        self.testapp.get('/apple_firmware/SERIAL', status=httplib.OK).body)

    self.assertEqual(password, resp['passphrase'])
    self.assertEqual(serial, resp['volume_uuid'])



class AppleFirmwarePasswordChangeOwnerTest(test_util.BaseTest):
  """Test the apple_firmware.AppleFirmwarePasswordChangeOwner class."""

  def setUp(self):
    super(AppleFirmwarePasswordChangeOwnerTest, self).setUp()

    settings.KEY_TYPE_DEFAULT_FILEVAULT = settings.KEY_TYPE_DATASTORE_FILEVAULT
    settings.KEY_TYPE_DEFAULT_XSRF = settings.KEY_TYPE_DATASTORE_XSRF

    self.user = base.User(
        key_name='stub7@example.com', user=users.User('stub7@example.com'))
    self.user.apple_firmware_perms = [permissions.CHANGE_OWNER]
    self.user.put()

    self.manufacturer = 'SampleManufacturer'
    self.serial = 'XX123456'
    self.platform_uuid = 'A4E75A65-FC39-441C-BEF5-49D9A3DC6BE0'

    self.volume_id = self._EscrowPassphrase('SECRET')
    self.testapp = webtest.TestApp(gae_main.app)

  def _EscrowPassphrase(self, passphrase):
    fvv = firmware.AppleFirmwarePassword(
        serial=self.serial,
        password=passphrase,
        hostname='somehost.local',
        platform_uuid=self.platform_uuid,
        created_by=users.User('stub7@example.com'))
    return fvv.put()

  @property
  def change_owner_url(self):
    return '/api/internal/change-owner/apple_firmware/%s/' % (self.volume_id)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testChangeOwner(self):
    self.testapp.post(self.change_owner_url, params={'new_owner': 'mew'},
                      status=httplib.OK)
    self.assertEqual(
        'mew@example.com', firmware.AppleFirmwarePassword.GetLatestForTarget(
            self.serial).owner)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testChangeOwnerForBadVolumeId(self):
    self.volume_id = 'bad-uuid'
    self.testapp.post(self.change_owner_url, params={'new_owner': 'mew'},
                      status=httplib.NOT_FOUND)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testChangeOwnerForNonexistantUuid(self):
    self.volume_id = db.Key.from_path('Testing', 'NonExistKeyTesting')
    self.testapp.post(self.change_owner_url, params={'new_owner': 'mew'},
                      status=httplib.NOT_FOUND)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testChangeOwnerForInactiveEntity(self):
    _ = self._EscrowPassphrase('NEW_SECRET')
    self.testapp.post(self.change_owner_url, params={'new_owner': 'mew'},
                      status=httplib.BAD_REQUEST)

  def testChangeOwnerWithoutValidXsrf(self):
    self.testapp.post(self.change_owner_url, params={'new_owner': 'mew'},
                      status=httplib.FORBIDDEN)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testChangeOwnerWithoutPermission(self):
    self.user.apple_firmware_perms = []
    self.user.put()
    self.testapp.post(self.change_owner_url, params={'new_owner': 'mew'},
                      status=httplib.FORBIDDEN)


if __name__ == '__main__':
  absltest.main()
