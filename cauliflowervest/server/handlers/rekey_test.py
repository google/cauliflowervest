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
#
import cauliflowervest.server.import_fixer
import httplib
import uuid

import webtest

from google.appengine.api import memcache

from google.apputils import basetest

from cauliflowervest.server import main as gae_main
from cauliflowervest.server import util
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import volumes as models


class RekeyModuleTest(test_util.BaseTest):

  def setUp(self):
    super(RekeyModuleTest, self).setUp()

    self.target_id = str(uuid.uuid4()).upper()

    self.v = models.LuksVolume(
        owner='stub7@example.com', volume_uuid=self.target_id, serial='stub',
        passphrase='SECRET', hdd_serial='stub', hostname='stub',
        platform_uuid='stub', active=True,
    )

    self.testapp = webtest.TestApp(gae_main.app)

  def testForceRekeying(self):
    self.v.force_rekeying = True
    self.v.put()

    resp = self.testapp.get(
        '/api/v1/rekey-required/luks/' + self.target_id, status=httplib.OK)

    self.assertTrue(util.FromSafeJson(resp.body))

  def testAccessDenied(self):
    self.testbed.setup_env(user_email='', user_id='', overwrite=True)
    self.v.put()

    self.testapp.get(
        '/api/v1/rekey-required/luks/' + self.target_id,
        status=httplib.FORBIDDEN)

  def testExperimentalRekey(self):
    target_id = 'missing'

    memcache.Client().set(target_id, 1, namespace='experimental_rekey')
    resp = self.testapp.get(
        '/api/v1/rekey-required/luks/' + target_id, status=httplib.OK)
    self.assertEqual(')]}\',\n"experimental"', resp.body)


if __name__ == '__main__':
  basetest.main()
