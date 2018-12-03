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

"""luks module tests."""

import httplib
import urllib



from absl.testing import absltest
import mock

from cauliflowervest.server import main as gae_main
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import luks
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import volumes


class NewLuksRequestHandlerTest(test_util.BaseTest):
  """Test the luks.Luks class."""

  def setUp(self):
    super(NewLuksRequestHandlerTest, self).setUp()

    self.c = luks.Luks()
    settings.KEY_TYPE_DEFAULT_XSRF = settings.KEY_TYPE_DATASTORE_XSRF

  def testPutWithValidXsrfToken(self, *_):
    volume_uuid = 'foovolumeuuid'
    params = {
        'xsrf-token': util.XsrfTokenGenerate('UploadPassphrase'),
        'hdd_serial': 'serial',
        'platform_uuid': 'uuid',
        'hostname': 'foohost'
        }

    resp = gae_main.app.get_response(
        '/luks/%s/?%s' % (volume_uuid, urllib.urlencode(params)),
        {'REQUEST_METHOD': 'PUT'},
        body='passphrase'
        )

    self.assertEqual(httplib.OK, resp.status_int)
    self.assertEqual('Secret successfully escrowed!', resp.body)

  def testPutWithInvalidXsrfToken(self, *_):
    volume_uuid = 'foovolumeuuid'
    params = {
        'xsrf-token': 'badtoken',
        'hdd_serial': 'serial',
        'platform_uuid': 'uuid',
        'hostname': 'foohost'
        }

    resp = gae_main.app.get_response(
        '/luks/%s/?%s' % (volume_uuid, urllib.urlencode(params)),
        {'REQUEST_METHOD': 'PUT'},
        body='passphrase'
        )

    self.assertEqual(httplib.FORBIDDEN, resp.status_int)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testPutWithMissingXsrfTokenAndProtectionDisabled(self, *_):
    volume_uuid = 'foovolumeuuid'
    params = {
        'hdd_serial': 'serial',
        'platform_uuid': 'uuid',
        'hostname': 'foohost'
        }

    resp = gae_main.app.get_response(
        '/luks/%s/?%s' % (volume_uuid, urllib.urlencode(params)),
        {'REQUEST_METHOD': 'PUT'},
        body='passphrase'
    )
    self.assertEqual(httplib.OK, resp.status_int)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testPutUnknown(self, *_):
    volume_uuid = 'foovolumeuuid'
    params = {
        'hdd_serial': 'serial',
        'platform_uuid': 'uuid',
        'hostname': 'foohost'
        }

    resp = gae_main.app.get_response(
        '/luks/%s/?%s' % (volume_uuid, urllib.urlencode(params)),
        {'REQUEST_METHOD': 'PUT'}
    )
    self.assertEqual(httplib.BAD_REQUEST, resp.status_int)
    self.assertEqual(
        'Unknown PUT',
        volumes.LuksAccessLog.all().fetch(10)[0].message
        )

  def testPutWithBrokenFormEncodedPassphrase(self, *_):
    mock_user = mock.MagicMock()
    mock_user.email = 'user@example.com'

    self.c.VerifyPermissions = mock.Mock(return_value=mock_user)
    self.c.VerifyXsrfToken = mock.Mock(return_value=True)
    self.c.PutNewSecret = mock.Mock(return_value=True)

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'

    self.c.request = mock.MagicMock()
    self.c.request.content_type = 'application/x-www-form-urlencoded'
    self.c.request.body = passphrase + '='
    self.c.request.get.return_value = ''

    self.c.put(volume_uuid)
    self.c.PutNewSecret.assert_called_once_with(
        mock_user.email, volume_uuid, passphrase, self.c.request)

  def testPutWithBase64EncodedPassphrase(self, *_):
    mock_user = mock.MagicMock()
    mock_user.email = 'user@example.com'

    self.c.VerifyPermissions = mock.Mock(return_value=mock_user)
    self.c.VerifyXsrfToken = mock.Mock(return_value=True)
    self.c.PutNewSecret = mock.Mock(return_value=True)

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase='

    self.c.request = mock.MagicMock()
    self.c.request.content_type = 'application/octet-stream'
    self.c.request.body = passphrase
    self.c.request.get.return_value = ''

    self.c.put(volume_uuid)
    self.c.PutNewSecret.assert_called_once_with(
        mock_user.email, volume_uuid, passphrase, self.c.request)


if __name__ == '__main__':
  absltest.main()
