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

from cauliflowervest.server import main as gae_main
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import base
from cauliflowervest.server.models import volumes as models


class CreatedModuleTest(test_util.BaseTest):

  def setUp(self):
    super(CreatedModuleTest, self).setUp()
    self.testapp = webtest.TestApp(gae_main.app)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testWalkthrough(self):
    models.ProvisioningVolume.created.auto_now = False

    vol_uuid1 = str(uuid.uuid4()).upper()
    secret1 = str(uuid.uuid4())

    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        provisioning_perms=[],
        ).put()

    models.ProvisioningVolume(
        owners=['stub'],
        created_by=users.get_current_user(),
        hdd_serial='stub',
        passphrase=secret1,
        created=datetime.datetime.now(),
        platform_uuid='stub',
        serial='stub',
        volume_uuid=vol_uuid1,
    ).put()

    old = datetime.datetime.now() - datetime.timedelta(days=365)
    models.ProvisioningVolume(
        owners=['stub1'],
        created_by=users.get_current_user(),
        hdd_serial='stub',
        passphrase=secret1,
        created=old,
        platform_uuid='stub',
        serial='stub',
        volume_uuid=str(uuid.uuid4()).upper()).put()

    resp = self.testapp.get('/created?json=1', status=httplib.OK)
    data = util.FromSafeJson(resp.body)

    self.assertEqual(1, len(data))
    self.assertEqual(secret1, data[0]['passphrase'])

    models.ProvisioningVolume.created.auto_now = True

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  @mock.patch.dict(
      settings.DEFAULT_PERMISSIONS, {permissions.TYPE_PROVISIONING: ()})
  def testAccessDenied(self):
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        provisioning_perms=[],
        ).put()

    self.testapp.get('/created?json=1', status=httplib.FORBIDDEN)


if __name__ == '__main__':
  absltest.main()
