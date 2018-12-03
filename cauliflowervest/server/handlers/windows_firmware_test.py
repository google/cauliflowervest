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

from cauliflowervest import settings as base_settings
from cauliflowervest.server import crypto
from cauliflowervest.server import main as gae_main
from cauliflowervest.server import service_factory
from cauliflowervest.server import services
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import firmware


class WindowsFirmwareHandlerTest(test_util.BaseTest):

  def setUp(self):
    super(WindowsFirmwareHandlerTest, self).setUp()

    self.testapp = webtest.TestApp(gae_main.app)
    inventory = service_factory.GetInventoryService()
    inventory.GetAssetTagsFromUploadRequest = mock.Mock(return_value=['111'])
    inventory.GetMetadataUpdates = mock.Mock(return_value={})

  def tearDown(self):
    service_factory.inventory_service = None
    super(WindowsFirmwareHandlerTest, self).tearDown()

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testUpload(self):
    password = 'S3cR3t6789'
    hostname = 'host1'
    serial = 'SERIAL'
    self.testapp.put(
        '/windows_firmware/?volume_uuid=%s&hostname=%s&smbios_guid=ID1' % (
            serial, hostname),
        params=password, status=httplib.OK)

    passwords = firmware.WindowsFirmwarePassword.all().fetch(None)

    self.assertEqual(1, len(passwords))
    self.assertEqual(password, passwords[0].password)
    self.assertEqual(serial, passwords[0].target_id)
    self.assertEqual(hostname, passwords[0].hostname)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testRetrieval(self):
    password = 'S3cR3t6789'
    hostname = 'host1'
    serial = 'SERIAL'
    firmware.WindowsFirmwarePassword(
        serial=serial, hostname=hostname, password=password, owner='stub7',
        smbios_guid='ID1',
    ).put()

    resp = util.FromSafeJson(
        self.testapp.get('/windows_firmware/SERIAL', status=httplib.OK).body)

    self.assertEqual(password, resp['passphrase'])
    self.assertEqual(serial, resp['volume_uuid'])



if __name__ == '__main__':
  absltest.main()
