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


class LinuxFirmwareHandlerTest(test_util.BaseTest):

  def setUp(self):
    super(LinuxFirmwareHandlerTest, self).setUp()

    self.testapp = webtest.TestApp(gae_main.app)
    inventory = service_factory.GetInventoryService()
    inventory.GetAssetTagsFromUploadRequest = mock.Mock(return_value=['111'])
    inventory.GetMetadataUpdates = mock.Mock(return_value={})

  def tearDown(self):
    service_factory.inventory_service = None
    super(LinuxFirmwareHandlerTest, self).tearDown()

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testUpload(self):
    password = '012'
    hostname = 'host1'
    serial = 'SERIAL'
    manufacturer = 'Vendor Inc.'
    machine_uuid = 'ID1'
    self.testapp.put(
        '/linux_firmware/?volume_uuid=%s&hostname=%s&machine_uuid=%s'
        '&manufacturer=%s' % (serial, hostname, machine_uuid, manufacturer),
        params=password, status=httplib.OK)

    passwords = firmware.LinuxFirmwarePassword.all().fetch(None)

    self.assertEqual(1, len(passwords))
    self.assertEqual(password, passwords[0].password)
    self.assertEqual(manufacturer+serial+machine_uuid, passwords[0].target_id)
    self.assertEqual(serial, passwords[0].serial)
    self.assertEqual(manufacturer, passwords[0].manufacturer)
    self.assertEqual(hostname, passwords[0].hostname)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testUploadMalformedSecrets(self):
    malformed_secrets = ['0123456789' '012345', '01', '01234!']
    for password in malformed_secrets:
      hostname = 'host1'
      serial = 'SERIAL'
      manufacturer = 'Vendor Inc.'
      machine_uuid = 'ID1'
      resp = self.testapp.put(
          '/linux_firmware/?volume_uuid=%s&hostname=%s&machine_uuid=%s'
          '&manufacturer=%s' % (serial, hostname, machine_uuid, manufacturer),
          params=password, status=httplib.BAD_REQUEST)
      resp.mustcontain('secret is malformed')

      passwords = firmware.LinuxFirmwarePassword.all().fetch(None)
      self.assertEqual(0, len(passwords))

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testRetrieval(self):
    password = 'S3cR3t6789'
    hostname = 'host1'
    serial = 'SERIAL'
    manufacturer = 'Vendor Inc.'
    machine_uuid = 'ID1'
    firmware.LinuxFirmwarePassword(
        serial=serial, hostname=hostname, password=password, owner='stub7',
        machine_uuid=machine_uuid, manufacturer=manufacturer
    ).put()

    resp = util.FromSafeJson(
        self.testapp.get('/linux_firmware/Vendor%20Inc.SERIALID1',
                         status=httplib.OK).body)

    self.assertEqual(password, resp['passphrase'])
    self.assertEqual(manufacturer+serial+machine_uuid, resp['volume_uuid'])



class LinuxFirmwarePasswordChangeOwnerTest(test_util.BaseTest):
  """Test the linux_firmware.LinuxFirmwarePasswordChangeOwner class."""

  def setUp(self):
    super(LinuxFirmwarePasswordChangeOwnerTest, self).setUp()

    settings.KEY_TYPE_DEFAULT_FILEVAULT = settings.KEY_TYPE_DATASTORE_FILEVAULT
    settings.KEY_TYPE_DEFAULT_XSRF = settings.KEY_TYPE_DATASTORE_XSRF

    self.user = base.User(
        key_name='stub7@example.com', user=users.User('stub7@example.com'))
    self.user.linux_firmware_perms = [permissions.CHANGE_OWNER]
    self.user.put()

    self.manufacturer = 'SampleManufacturer Inc.'
    self.serial = 'XX123456'
    self.machine_uuid = 'A4E75A65-FC39-441C-BEF5-49D9A3DC6BE0'

    self.volume_id = self._EscrowPassphrase('SECRET')

  def _EscrowPassphrase(self, passphrase):
    fvv = firmware.LinuxFirmwarePassword(
        manufacturer=self.manufacturer,
        serial=self.serial,
        password=passphrase,
        hostname='somehost.local',
        machine_uuid=self.machine_uuid,
        created_by=users.User('stub7@example.com'))
    return fvv.put()

  @property
  def change_owner_url(self):
    return '/api/internal/change-owner/linux_firmware/%s/' % (self.volume_id)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testChangeOwner(self):
    resp = gae_main.app.get_response(
        self.change_owner_url,
        {'REQUEST_METHOD': 'POST'},
        POST={'new_owner': 'mew'})
    self.assertEqual(httplib.OK, resp.status_int)
    self.assertEqual(
        'mew@example.com', firmware.LinuxFirmwarePassword.GetLatestForTarget(
            self.manufacturer+self.serial+self.machine_uuid).owner)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testChangeOwnerForBadVolumeId(self):
    self.volume_id = 'bad-uuid'
    resp = gae_main.app.get_response(
        self.change_owner_url,
        {'REQUEST_METHOD': 'POST'},
        POST={'new_owner': 'mew'})
    self.assertEqual(httplib.NOT_FOUND, resp.status_int)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testChangeOwnerForNonexistantUuid(self):
    self.volume_id = db.Key.from_path('Testing', 'NonExistKeyTesting')
    resp = gae_main.app.get_response(
        self.change_owner_url,
        {'REQUEST_METHOD': 'POST'},
        POST={'new_owner': 'mew'})
    self.assertEqual(httplib.NOT_FOUND, resp.status_int)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testChangeOwnerForInactiveEntity(self):
    _ = self._EscrowPassphrase('NEW_SECRET')
    resp = gae_main.app.get_response(
        self.change_owner_url,
        {'REQUEST_METHOD': 'POST'},
        POST={'new_owner': 'mew'})
    self.assertEqual(httplib.BAD_REQUEST, resp.status_int)

  def testChangeOwnerWithoutValidXsrf(self):
    resp = gae_main.app.get_response(
        self.change_owner_url,
        {'REQUEST_METHOD': 'POST'},
        POST={'new_owner': 'mew'})
    self.assertEqual(httplib.FORBIDDEN, resp.status_int)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testChangeOwnerWithoutPermission(self):
    self.user.linux_firmware_perms = []
    self.user.put()
    resp = gae_main.app.get_response(
        self.change_owner_url,
        {'REQUEST_METHOD': 'POST'},
        POST={'new_owner': 'mew'})
    self.assertEqual(httplib.FORBIDDEN, resp.status_int)


if __name__ == '__main__':
  absltest.main()
