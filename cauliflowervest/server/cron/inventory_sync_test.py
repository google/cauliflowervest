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

from absl.testing import absltest
import mock
import webtest

from cauliflowervest.server import service_factory
from cauliflowervest.server import services
from cauliflowervest.server.cron import inventory_sync
from cauliflowervest.server.cron import main as gae_main
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import firmware
from cauliflowervest.server.models import volumes


class InventorySyncTest(test_util.BaseTest):

  def setUp(self):
    super(InventorySyncTest, self).setUp()

    self.testapp = webtest.TestApp(gae_main.app)

  @mock.patch.object(
      service_factory, 'GetInventoryService', spec=services.InventoryService)
  def testUpdateHostnameAppleFirmaware(self, factory_mock):
    new_hostname = 'somethingelse'
    factory_mock.return_value.GetMetadataUpdates.return_value = {
        'hostname': new_hostname,
        'non_existing_property': 112,
    }

    test_util.MakeAppleFirmware(save=True, hostname='hostname1')
    self.testapp.get('/cron/inventory_sync')

    test_util.RunAllDeferredTasks(self.testbed)

    entities = firmware.AppleFirmwarePassword.all().fetch(10)
    self.assertEqual(1, len(entities))

    self.assertEqual(new_hostname, entities[0].hostname)

  @mock.patch.dict(inventory_sync.__dict__, {'_BATCH_SIZE': 1})
  @mock.patch.object(
      service_factory, 'GetInventoryService', spec=services.InventoryService)
  def testUpdateHostnameLinuxFirmaware(self, factory_mock):
    new_hostname = 'somethingelse'
    factory_mock.return_value.GetMetadataUpdates.return_value = {
        'hostname': new_hostname,
        'non_existing_property': 112,
    }

    test_util.MakeLinuxFirmware(save=True, hostname='hostname1')
    test_util.MakeLinuxFirmware(save=True, hostname='hostname2')
    self.testapp.get('/cron/inventory_sync')

    test_util.RunAllDeferredTasks(self.testbed)
    test_util.RunAllDeferredTasks(self.testbed)

    entities = firmware.LinuxFirmwarePassword.all().fetch(10)
    self.assertEqual(2, len(entities))

    self.assertEqual(new_hostname, entities[0].hostname)

  @mock.patch.object(
      service_factory, 'GetInventoryService', spec=services.InventoryService)
  def testUpdateOwner(self, factory_mock):
    new_owner = 'plague'
    factory_mock.return_value.GetMetadataUpdates.return_value = {
        'owners': [new_owner],
    }

    test_util.MakeAppleFirmware(save=True, owner='acidburn')
    self.testapp.get('/cron/inventory_sync')

    test_util.RunAllDeferredTasks(self.testbed)

    entities = firmware.AppleFirmwarePassword.all().fetch(10)
    self.assertEqual(1, len(entities))

    self.assertEqual(new_owner + '@example.com', entities[0].owner)
    self.assertTrue(entities[0].force_rekeying)

  @mock.patch.object(
      service_factory, 'GetInventoryService', spec=services.InventoryService)
  def testUpdateOwnerBitlocker(self, factory_mock):
    new_owner = 'plague'
    factory_mock.return_value.GetMetadataUpdates.return_value = {
        'owners': [new_owner],
    }

    test_util.MakeBitLockerVolume(save=True, owner='acidburn')
    self.testapp.get('/cron/inventory_sync')

    test_util.RunAllDeferredTasks(self.testbed)

    entities = volumes.BitLockerVolume.all().fetch(10)
    self.assertEqual(1, len(entities))

    self.assertEqual(new_owner + '@example.com', entities[0].owner)
    self.assertTrue(entities[0].force_rekeying)


if __name__ == '__main__':
  absltest.main()
