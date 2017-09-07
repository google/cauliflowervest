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
import collections
import httplib



import mock

from google.appengine.api import users

from google.apputils import basetest

from cauliflowervest.server import main as gae_main
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import base_handler
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import base


class VolumeTypesModuleTest(test_util.BaseTest):

  def testOk(self):
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        filevault_perms=[permissions.SEARCH], luks_perms=[permissions.SEARCH],
    ).put()

    resp = gae_main.app.get_response(
        '/api/internal/volume_types', {'REQUEST_METHOD': 'GET'})

    self.assertEqual(httplib.OK, resp.status_int)

    data = util.FromSafeJson(resp.body)
    volume_fields = {x: y for x, y in data.items() if 'fields' in y}
    self.assertEqual(2, len(volume_fields))

  @mock.patch.object(
      base_handler, 'VerifyAllPermissionTypes',
      return_value=collections.defaultdict(lambda: False))
  def testOkStatusWithoutPermissions(self, *_):
    resp = gae_main.app.get_response(
        '/api/internal/volume_types', {'REQUEST_METHOD': 'GET'})

    self.assertEqual(httplib.OK, resp.status_int)

    self.assertEqual(0, len(util.FromSafeJson(resp.body)))

  @mock.patch.dict(
      settings.__dict__, {
          'DEFAULT_PERMISSIONS': {
              permissions.TYPE_LUKS: (permissions.RETRIEVE_OWN)
          }
      })
  def testNoSearchPermissionsCanRetrieveOwn(self):
    resp = gae_main.app.get_response(
        '/api/internal/volume_types', {'REQUEST_METHOD': 'GET'})

    self.assertEqual(httplib.OK, resp.status_int)

    data = util.FromSafeJson(resp.body)
    self.assertEqual('stub7', data['user'])
    self.assertEqual(2, len(data))
    self.assertEqual(
        [permissions.RETRIEVE_OWN], data[permissions.TYPE_LUKS].keys())
    self.assertTrue(data[permissions.TYPE_LUKS][permissions.RETRIEVE_OWN])


if __name__ == '__main__':
  basetest.main()
