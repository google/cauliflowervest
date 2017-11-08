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



import mock

from google.appengine.ext import deferred
from google.appengine.ext import testbed

from absl.testing import absltest

from cauliflowervest.server import settings
from cauliflowervest.server.handlers import provisioning
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import volumes as models


class ProvisioningHandlerTest(test_util.BaseTest):
  """Test the filevault.FileVault class."""

  def testPutNonNormalizedHostname(self):
    request = mock.MagicMock()
    p = provisioning.Provisioning(request)

    hostname = 'mixed-CASE'
    volume = p._CreateNewSecretEntity('OWNER1', 'UUID-1234-12', 'SECRET55')
    volume.hostname = hostname
    volume.hdd_serial = 'DOES_NOT_MATTER'
    volume.serial = 'DOES_NOT_MATTER'
    volume.platform_uuid = 'DOES_NOT_MATTER'
    volume.put()

    volumes = models.ProvisioningVolume.all().fetch(2)
    self.assertEqual(1, len(volumes))
    self.assertEqual(
        models.ProvisioningVolume.NormalizeHostname(hostname),
        volumes[0].hostname)



if __name__ == '__main__':
  absltest.main()
