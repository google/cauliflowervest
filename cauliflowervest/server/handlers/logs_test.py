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
import mock
import webtest

from absl.testing import absltest

from cauliflowervest.server import main as gae_main
from cauliflowervest.server import util
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import volumes


class LogsModuleTest(test_util.BaseTest):

  def setUp(self):
    super(LogsModuleTest, self).setUp()

    self.volume = volumes.LuksVolume(
        owner='stub', hdd_serial='stub', hostname='stub', passphrase='secret',
        platform_uuid='stub', volume_uuid='vol_uuid'
    )

    self.testapp = webtest.TestApp(gae_main.app)

  @mock.patch.object(base_handler, 'VerifyPermissions')
  def testLog(self, _):
    self.volume.put()
    volumes.LuksAccessLog.Log(entity=self.volume, message='PUT')

    resp = util.FromSafeJson(self.testapp.get('/logs?log_type=luks').body)

    self.assertEqual('luks', resp['log_type'])
    self.assertEqual(1, len(resp['logs']))


if __name__ == '__main__':
  absltest.main()
