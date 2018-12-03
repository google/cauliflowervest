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

import datetime
import httplib
import uuid



from absl.testing import absltest
import mock
import webtest

from google.appengine.api import users
from google.appengine.ext import deferred
from google.appengine.ext import testbed


from cauliflowervest.server import main as gae_main
from cauliflowervest.server import settings
from cauliflowervest.server.handlers import maintenance
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import volumes as models


class MaintenanceModuleTest(test_util.BaseTest):

  def setUp(self):
    super(MaintenanceModuleTest, self).setUp()

    self.testapp = webtest.TestApp(gae_main.app)

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

    resp = self.testapp.get('/api/internal/maintenance/update_volumes_schema')

    self.assertEqual(200, resp.status_int)

    taskqueue = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
    tasks = taskqueue.get_filtered_tasks()
    self.assertEqual(8, len(tasks))

    for task in tasks:
      deferred.run(task.payload)

    self.assertEqual('v1', models.ProvisioningVolume.all().fetch(1)[0].tag)

  @mock.patch.dict(
      settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  @mock.patch.object(
      maintenance.users, 'is_current_user_admin', return_value=False)
  def testAccessDenied(self, _):
    self.testapp.get(
        '/api/internal/maintenance/update_volumes_schema',
        status=httplib.FORBIDDEN)


if __name__ == '__main__':
  absltest.main()
