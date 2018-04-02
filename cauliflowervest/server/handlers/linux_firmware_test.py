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

import mock
import webtest

from absl.testing import absltest

from cauliflowervest import settings as base_settings
from cauliflowervest.server import crypto
from cauliflowervest.server import main as gae_main
from cauliflowervest.server import service_factory
from cauliflowervest.server import services
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import firmware


class LinuxFirmwareHandlerTest(test_util.BaseTest):

  def setUp(self):
    super(LinuxFirmwareHandlerTest, self).setUp()

    self.testapp = webtest.TestApp(gae_main.app)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testUpload(self):
    password = '012'
    hostname = 'host1'
    serial = 'SERIAL'
    manufacturer = 'Vendor'
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
      manufacturer = 'Vendor'
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
    manufacturer = 'Vendor'
    machine_uuid = 'ID1'
    firmware.LinuxFirmwarePassword(
        serial=serial, hostname=hostname, password=password, owner='stub7',
        machine_uuid=machine_uuid, manufacturer=manufacturer
    ).put()

    resp = util.FromSafeJson(
        self.testapp.get('/linux_firmware/VendorSERIALID1',
                         status=httplib.OK).body)

    self.assertEqual(password, resp['passphrase'])
    self.assertEqual(manufacturer+serial+machine_uuid, resp['volume_uuid'])



if __name__ == '__main__':
  absltest.main()
