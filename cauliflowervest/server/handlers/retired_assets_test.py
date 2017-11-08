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

from cauliflowervest.server import main as gae_main
from cauliflowervest.server import service_factory
from cauliflowervest.server import services
from cauliflowervest.server import util
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.handlers import test_util


class RetiredAssetsModuleTest(test_util.BaseTest):

  def setUp(self):
    super(RetiredAssetsModuleTest, self).setUp()

    self.testapp = webtest.TestApp(gae_main.app)

  @mock.patch.object(base_handler, 'VerifyPermissions')
  @mock.patch.object(service_factory, 'GetInventoryService')
  def testSuccess(self, factory_mock, _):
    inventory_service_mock = mock.Mock(spec=services.InventoryService)
    factory_mock.return_value = inventory_service_mock
    inventory_service_mock.IsRetiredMac.side_effect = lambda s: s == '1234'

    test_util.MakeAppleFirmware(serial='1234')
    test_util.MakeAppleFirmware(serial='231')

    response = self.testapp.get('/api/internal/retired-assets/1234,231')

    res = util.FromSafeJson(response.body)
    self.assertEqual(['231'], res['active'])
    self.assertEqual(
        [{'password': '123456789', 'serial': '1234'}],
        res['retired'])

  def testAccessDenied(self):
    test_util.MakeAppleFirmware(serial='1234')
    test_util.MakeAppleFirmware(serial='231')

    self.testapp.get(
        '/api/internal/retired-assets/1234,231', status=httplib.FORBIDDEN)


if __name__ == '__main__':
  absltest.main()
