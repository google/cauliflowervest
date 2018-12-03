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

"""Tests for client module."""

import cookielib
import httplib
import StringIO
import time
import urllib2



from absl.testing import absltest
import mock
import oauth2client.client

from cauliflowervest.client import base_client


def GetArgFromCallHistory(mock_fn, call_index=0, arg_index=0):
  return mock_fn.call_args_list[call_index][0][arg_index]


class CauliflowerVestClientTest(absltest.TestCase):
  """Test the base_client.CauliflowerVestClient class."""

  def setUp(self):
    super(CauliflowerVestClientTest, self).setUp()
    base_client.CauliflowerVestClient.ESCROW_PATH = 'foobar'
    self.headers = {'fooheader': 'foovalue'}
    self.c = base_client.CauliflowerVestClient(
        'http://example.com', None, headers=self.headers)

  def testGetAndValidateMetadata(self):
    self.c.REQUIRED_METADATA = ['foo', 'bar']

    with mock.patch.object(
        self.c, '_GetMetadata', return_value={'foo': 'asdf', 'bar': 'qwerty'}):
      self.c.GetAndValidateMetadata()

  def testGetAndValidateMetadataWithError(self):
    self.c.REQUIRED_METADATA = ['foo', 'bar']

    with mock.patch.object(
        self.c, '_GetMetadata', return_value={'foo': 'asdf'}):
      with self.assertRaisesRegexp(
          base_client.MetadataError, r'Required metadata is not found: bar'):
        self.c.GetAndValidateMetadata()

  def testRetryRequest(self):
    self.c.opener = mock.Mock(spec=urllib2.OpenerDirector)
    self.c.opener.open.return_value = httplib.OK
    mock_request = mock.Mock(spec=base_client.fancy_urllib.FancyRequest)

    ret = self.c._RetryRequest(mock_request, 'foo desc')

    self.assertEqual(ret, httplib.OK)
    for k, v in self.headers.iteritems():
      mock_request.add_header.assert_called_with(k, v)

  def testRetryRequestURLError(self):
    with mock.patch.object(
        self.c, 'opener', spec=urllib2.OpenerDirector) as mock_o:
      mock_o.open.side_effect = base_client.urllib2.URLError('some problem')
      mock_request = mock.Mock(spec=base_client.fancy_urllib.FancyRequest)

      with self.assertRaisesRegexp(
          base_client.RequestError,
          r'foo failed permanently: <urlopen error some problem>'):
        self.c._RetryRequest(mock_request, 'foo')

  def testRetryRequest404(self):
    self.c.opener = mock.Mock(spec=urllib2.OpenerDirector)

    mock_fp = StringIO.StringIO('Detailed error message.')
    err = base_client.urllib2.HTTPError(
        'url', 404, httplib.responses[404], {}, mock_fp)
    self.c.opener.open.side_effect = err

    mock_request = mock.Mock(spec=base_client.fancy_urllib.FancyRequest)

    with self.assertRaisesRegexp(
        base_client.RequestError,
        r'foo failed: HTTP Error 404: Not Found: Detailed error message.'):
      self.c._RetryRequest(mock_request, 'foo')

  def testRetryRequest404WithArgument(self):
    self.c.opener = mock.Mock(spec=urllib2.OpenerDirector)

    mock_fp = StringIO.StringIO('Detailed error message.')
    err = base_client.urllib2.HTTPError(
        'url', 404, httplib.responses[404], {}, mock_fp)
    self.c.opener.open.side_effect = [err, httplib.OK]

    mock_request = mock.Mock(spec=base_client.fancy_urllib.FancyRequest)

    self.assertEqual(self.c._RetryRequest(mock_request, 'foo', retry_4xx=True),
                     httplib.OK)

  @mock.patch.object(time, 'sleep')
  def testRetryRequestRequestError(self, sleep_mock):
    self.c.opener = mock.Mock(spec=urllib2.OpenerDirector)
    mock_fp = StringIO.StringIO('Detailed error message.')
    err = base_client.urllib2.HTTPError(
        'url', 500, httplib.responses[500], {}, mock_fp)
    self.c.opener.open.side_effect = err

    mock_request = mock.Mock(spec=base_client.fancy_urllib.FancyRequest)

    with self.assertRaisesRegexp(
        base_client.RequestError,
        r'foo2 failed permanently: HTTP Error 500: Internal Server Error: '
        r'Detailed error message.'):
      self.c._RetryRequest(mock_request, 'foo2')

    for i in xrange(0, self.c.MAX_TRIES - 1):
      sleep_mock.assert_has_calls(
          [mock.call((i + 1) * self.c.TRY_DELAY_FACTOR)])

  def testFetchXsrfToken(self):
    mock_response = mock.Mock()
    mock_response.read.return_value = 'mock-xsrf-token'

    self.c.opener = mock.Mock(spec=urllib2.OpenerDirector)
    self.c.opener.open.return_value = mock_response

    self.assertEquals('mock-xsrf-token', self.c._FetchXsrfToken('Action'))

  def testIsKeyRotationNeeded(self):
    self.c.opener = mock.Mock(spec=urllib2.OpenerDirector)

    self.c.opener.open.return_value.code = httplib.OK
    self.c.opener.open.return_value.read.return_value = (
        base_client.JSON_PREFIX + 'true')

    self.assertTrue(self.c.IsKeyRotationNeeded('UUID'))

    self.assertEqual(
        'http://example.com/api/v1/rekey-required/foobar/UUID?tag=default',
        self.c.opener.open.call_args_list[0][0][0].get_full_url())

  def testIsKeyRotationNeededRequestError(self):
    self.c.opener = mock.Mock(spec=urllib2.OpenerDirector)
    mock_fp = StringIO.StringIO('Detailed error message.')
    err = base_client.urllib2.HTTPError(
        'url', 500, httplib.responses[500], {}, mock_fp)
    self.c.opener.open.side_effect = err

    with self.assertRaisesRegexp(
        base_client.RequestError,
        r'Failed to get status. HTTP Error 500: Internal Server Error: '
        r'Detailed error message.'):
      self.c.IsKeyRotationNeeded('UUID')

  def testIsKeyRotationNeededURLError(self):
    with mock.patch.object(
        self.c, 'opener', spec=urllib2.OpenerDirector) as mock_o:
      mock_o.open.side_effect = base_client.urllib2.URLError('some problem')

      with self.assertRaisesRegexp(
          base_client.RequestError,
          r'Failed to get status. <urlopen error some problem>'):
        self.c.IsKeyRotationNeeded('UUID')

  def _RetrieveTest(self, code, read=True):
    self.volume_uuid = 'foostrvolumeuuid'
    self.passphrase = 'foopassphrase'
    content = '{"passphrase": "%s"}' % self.passphrase

    self.c._FetchXsrfToken = mock.Mock()
    self.c._FetchXsrfToken.return_value = 'token'

    self.c.opener = mock.Mock(spec=urllib2.OpenerDirector)
    if code == httplib.OK:
      mock_response = mock.Mock()
      self.c.opener.open.return_value = mock_response
      mock_response.code = code
      if read:
        mock_response.read.return_value = base_client.JSON_PREFIX + content
    else:
      mock_fp = StringIO.StringIO('Detailed error message for %s.' % code)
      exc = base_client.urllib2.HTTPError(
          'url', code, httplib.responses[code], {}, mock_fp)
      self.c.opener.open.side_effect = exc

  def testRetrieveSecret(self):
    self._RetrieveTest(httplib.OK)

    ret = self.c.RetrieveSecret('foo')
    self.assertEqual(ret, self.passphrase)

    self.assertEqual(
        'RetrieveSecret', GetArgFromCallHistory(self.c._FetchXsrfToken))

  def testRetrieveSecretNotFoundError(self):
    self._RetrieveTest(404)

    with self.assertRaisesRegexp(
        base_client.NotFoundError,
        r'Failed to retrieve passphrase. HTTP Error 404: Not Found: '
        r'Detailed error message for 404.'):
      self.c.RetrieveSecret(self.volume_uuid)

  def testRetrieveSecretRequestError(self):
    self._RetrieveTest(403)

    with self.assertRaisesRegexp(
        base_client.RequestError,
        r'Failed to retrieve passphrase. HTTP Error 403: Forbidden: '
        r'Detailed error message for 403.'):
      self.c.RetrieveSecret(self.volume_uuid)

  def testRetrieveSecretURLError(self):
    with mock.patch.object(
        self.c, '_FetchXsrfToken', return_value='token'), mock.patch.object(
            self.c, 'opener', spec=urllib2.OpenerDirector) as mock_o:
      mock_o.open.side_effect = base_client.urllib2.URLError('some problem')

      with self.assertRaisesRegexp(
          base_client.RequestError,
          r'Failed to retrieve passphrase. <urlopen error some problem>'):
        self.c.RetrieveSecret('SomeVolume')

  def _UploadTest(self, codes):
    self.c._GetMetadata = mock.Mock(return_value={'foo': 'bar'})
    self.c._FetchXsrfToken = mock.Mock(return_value='token')

    side_effect = []
    for code in codes:
      if code == httplib.OK:
        mock_response = mock.Mock()
        mock_response.code = code

        side_effect.append(mock_response)
      else:
        mock_fp = StringIO.StringIO('Detailed error message for %s.' % code)
        exc = base_client.urllib2.HTTPError(
            'url', code, httplib.responses[code], {}, mock_fp)
        side_effect.append(exc)

    self.c.opener = mock.Mock(spec=urllib2.OpenerDirector)
    self.c.opener.open.side_effect = side_effect

  def testUploadPassphrase(self):
    self._UploadTest([httplib.OK])
    self.c.UploadPassphrase('foo', 'bar')

    self.c._FetchXsrfToken.assert_called_once_with('UploadPassphrase')

  @mock.patch.object(time, 'sleep')
  def testUploadPassphraseWithTransientRequestError(self, sleep_mock):
    self._UploadTest([httplib.INTERNAL_SERVER_ERROR,
                      httplib.INTERNAL_SERVER_ERROR, httplib.OK])

    self.c.UploadPassphrase('foo', 'bar')

    self.assertEqual(2, sleep_mock.call_count)

  @mock.patch.object(time, 'sleep')
  def testUploadPassphraseWithRequestError(self, sleep_mock):
    self._UploadTest([403])

    with self.assertRaisesRegexp(
        base_client.RequestError,
        r'Uploading passphrase failed: HTTP Error 403: Forbidden: '
        r'Detailed error message for 403.'):
      self.c.UploadPassphrase('foo', 'bar')

    sleep_mock.assert_not_called()

  @mock.patch.object(time, 'sleep')
  def testUploadPassphraseWithServerError(self, sleep_mock):
    reqs = []
    for _ in xrange(0, 5):
      reqs.append(httplib.INTERNAL_SERVER_ERROR)
    self._UploadTest(reqs)

    with self.assertRaisesRegexp(
        base_client.RequestError,
        r'Uploading passphrase failed permanently: HTTP Error 500: '
        r'Internal Server Error: Detailed error message for 500.'):
      self.c.UploadPassphrase('foo', 'bar')

    self.assertEqual(4, sleep_mock.call_count)




class BuildOauth2OpenerTest(absltest.TestCase):

  def testSuccess(self):
    creds = mock.Mock(spec=oauth2client.client.Credentials)

    opener = base_client.BuildOauth2Opener(creds)

    self.assertIsInstance(opener, urllib2.OpenerDirector)
    self.assertIsInstance(GetArgFromCallHistory(creds.apply, 0, 0), dict)


if __name__ == '__main__':
  absltest.main()
