#!/usr/bin/env python
#
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
#
import datetime
import uuid


import mock

from google.appengine.api import users
from google.appengine.ext import deferred
from google.appengine.ext import testbed

from google.apputils import app
from google.apputils import basetest

from cauliflowervest.server import main as gae_main
from cauliflowervest.server import settings
from cauliflowervest.server.handlers import maintenance
from tests.cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import volumes as models


class MaintenanceModuleTest(basetest.TestCase):

  def setUp(self):
    super(MaintenanceModuleTest, self).setUp()
    test_util.SetUpTestbedTestCase(self)

  def tearDown(self):
    super(MaintenanceModuleTest, self).tearDown()
    test_util.TearDownTestbedTestCase(self)

  @mock.patch.dict(
      settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  @mock.patch.object(
      maintenance.users, 'is_current_user_admin', return_value=True)
  def testWalkthrough(self, _):
    models.ProvisioningVolume(
        owner='stub', created_by=users.get_current_user(),
        hdd_serial='stub', passphrase=str(uuid.uuid4()),
        created=datetime.datetime.now(), platform_uuid='stub',
        serial='stub', volume_uuid=str(uuid.uuid4()).upper(), tag='v1'
    ).put()

    resp = gae_main.app.get_response(
        '/api/internal/maintenance/update_volumes_schema',
        {'REQUEST_METHOD': 'GET'})

    self.assertEqual(200, resp.status_int)

    taskqueue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
    tasks = taskqueue.get_filtered_tasks()
    self.assertEqual(4, len(tasks))

    for task in tasks:
      deferred.run(task.payload)

    self.assertEqual('v1', models.ProvisioningVolume.all().fetch(1)[0].tag)


def main(_):
  basetest.main()


if __name__ == '__main__':
  app.run()
