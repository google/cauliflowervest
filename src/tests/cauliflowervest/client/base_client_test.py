#!/usr/bin/env python
#
# Copyright 2011 Google Inc. All Rights Reserved.
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

"""Tests for client module."""



import cookielib
import unittest
import urllib2

import mox
import stubout

from cauliflowervest.client import base_client


class CauliflowerVestClientTest(mox.MoxTestBase):
  """Test the base_client.CauliflowerVestClient class."""

  def setUp(self):
    super(CauliflowerVestClientTest, self).setUp()
    self.mox = mox.Mox()
    base_client.CauliflowerVestClient.ESCROW_PATH = 'foobar'
    self.mock_opener = self.mox.CreateMockAnything()
    self.headers = {'fooheader': 'foovalue'}
    self.c = base_client.CauliflowerVestClient(
        'http://example.com', self.mock_opener, headers=self.headers)

  def tearDown(self):
    self.mox.UnsetStubs()

  def testGetAndValidateMetadata(self):
    self.c.REQUIRED_METADATA = ['foo', 'bar']
    self.mox.StubOutWithMock(self.c, '_GetMetadata')
    self.c._GetMetadata().AndReturn({'foo': 'asdf', 'bar': 'qwerty'})
    self.mox.ReplayAll()
    self.c.GetAndValidateMetadata()
    self.mox.VerifyAll()

  def testGetAndValidateMetadataWithError(self):
    self.c.REQUIRED_METADATA = ['foo', 'bar']
    self.mox.StubOutWithMock(self.c, '_GetMetadata')
    self.c._GetMetadata().AndReturn({'foo': 'asdf'})
    self.mox.ReplayAll()
    self.assertRaises(base_client.MetadataError, self.c.GetAndValidateMetadata)
    self.mox.VerifyAll()

  def testRetryRequest(self):
    self.c.opener = self.mox.CreateMockAnything()
    mock_request = self.mox.CreateMockAnything()
    for k, v in self.headers.iteritems():
      mock_request.add_header(k, v).AndReturn(None)
    self.c.opener.open(mock_request).AndReturn('200')

    self.mox.ReplayAll()
    ret = self.c._RetryRequest(mock_request, 'foo desc')
    self.assertEqual(ret, '200')
    self.mox.VerifyAll()

  def testRetryRequest404(self):
    self.c.opener = self.mox.CreateMockAnything()
    mock_fp = self.mox.CreateMockAnything()
    err = base_client.urllib2.HTTPError('url', 404, 'HTTP Err 404', {}, mock_fp)
    mock_request = self.mox.CreateMockAnything()
    for k, v in self.headers.iteritems():
      mock_request.add_header(k, v).AndReturn(None)
    self.c.opener.open(mock_request).AndRaise(err)

    self.mox.ReplayAll()
    self.assertRaises(
        base_client.urllib2.HTTPError, self.c._RetryRequest,
        mock_request, 'foo')
    self.mox.VerifyAll()

  def testRetryRequestRequestError(self):
    self.mox.StubOutWithMock(base_client.time, 'sleep')
    self.c.opener = self.mox.CreateMockAnything()
    mock_fp = self.mox.CreateMockAnything()
    err = base_client.urllib2.HTTPError('url', 500, 'HTTP Err 500', {}, mock_fp)
    mock_request = self.mox.CreateMockAnything()

    for k, v in self.headers.iteritems():
      mock_request.add_header(k, v).AndReturn(None)
    self.c.opener.open(mock_request).AndRaise(err)
    for i in xrange(0, self.c.MAX_TRIES - 1):
      base_client.time.sleep((i + 1) * self.c.TRY_DELAY_FACTOR)
      self.c.opener.open(mock_request).AndRaise(err)

    self.mox.ReplayAll()
    self.assertRaises(
        base_client.RequestError, self.c._RetryRequest, mock_request, 'foo')
    self.mox.VerifyAll()

  def testFetchXsrfToken(self):
    self.c.opener = self.mox.CreateMockAnything()
    mock_response = self.mox.CreateMockAnything()
    mock_response.read().AndReturn('mock-xsrf-token')
    self.c.opener.open(
        mox.IsA(base_client.fancy_urllib.FancyRequest)).AndReturn(mock_response)
    self.mox.ReplayAll()
    self.assertEquals('mock-xsrf-token', self.c._FetchXsrfToken('Action'))

  def _RetrieveTest(self, code, read=True):
    self.volume_uuid = 'foostrvolumeuuid'
    self.passphrase = 'foopassphrase'
    content = '{"passphrase": "%s"}' % self.passphrase

    self.mox.StubOutWithMock(self.c, '_FetchXsrfToken')
    self.c._FetchXsrfToken('RetrieveSecret').AndReturn('token')

    if code == 200:
      mock_response = self.mox.CreateMockAnything()
      self.mock_opener.open(
          mox.IsA(base_client.fancy_urllib.FancyRequest)).AndReturn(
              mock_response)
      mock_response.code = code
      if read:
        mock_response.read().AndReturn(base_client.JSON_PREFIX + content)
    else:
      mock_fp = self.mox.CreateMockAnything()
      exc = base_client.urllib2.HTTPError(
          'url', code, 'HTTP Error %s' % code, {}, mock_fp)
      self.mock_opener.open(
          mox.IsA(base_client.fancy_urllib.FancyRequest)).AndRaise(exc)

  def testRetrieveSecret(self):
    self._RetrieveTest(200)
    self.mox.ReplayAll()
    ret = self.c.RetrieveSecret('foo')
    self.assertEqual(ret, self.passphrase)
    self.mox.VerifyAll()

  def testRetrieveSecretRequestError(self):
    self._RetrieveTest(403)
    self.mox.ReplayAll()
    self.assertRaises(
        base_client.RequestError,
        self.c.RetrieveSecret, self.volume_uuid)
    self.mox.VerifyAll()

  def _UploadTest(self, code):
    self.mox.StubOutWithMock(self.c, 'GetAndValidateMetadata')
    self.mox.StubOutWithMock(self.c, '_FetchXsrfToken')
    self.mox.StubOutWithMock(self.c, '_GetMetadata')

    def MetadataSideEffects():
      self.c._metadata = {'foo': 'bar'}

    self.c._FetchXsrfToken('UploadPassphrase').AndReturn('token')
    self.c.GetAndValidateMetadata().WithSideEffects(MetadataSideEffects)
    self._UploadTestReq(code)

  def _UploadTestReq(self, code):
    if code == 200:
      mock_response = self.mox.CreateMockAnything()
      mock_response.code = code
      self.mock_opener.open(
          mox.IsA(base_client.fancy_urllib.FancyRequest)).AndReturn(
              mock_response)
    else:
      mock_fp = self.mox.CreateMockAnything()
      exc = base_client.urllib2.HTTPError(
          'url', code, 'HTTP Error %s' % code, {}, mock_fp)
      self.mock_opener.open(
          mox.IsA(base_client.fancy_urllib.FancyRequest)).AndRaise(exc)

  def testUploadPassphrase(self):
    self._UploadTest(200)
    self.mox.ReplayAll()
    self.c.UploadPassphrase('foo', 'bar')
    self.mox.VerifyAll()

  def testUploadPassphraseWithTransientRequestError(self):
    self.mox.StubOutWithMock(base_client.time, 'sleep')
    self._UploadTest(500)
    base_client.time.sleep(mox.IsA(int))
    self._UploadTestReq(500)
    base_client.time.sleep(mox.IsA(int))
    self._UploadTestReq(200)

    self.mox.ReplayAll()
    self.c.UploadPassphrase('foo', 'bar')
    self.mox.VerifyAll()

  def testUploadPassphraseWithRequestError(self):
    self.mox.StubOutWithMock(base_client.time, 'sleep')
    self._UploadTest(403)

    self.mox.ReplayAll()
    self.assertRaises(
        urllib2.HTTPError,
        self.c.UploadPassphrase, 'foo', 'bar')
    self.mox.VerifyAll()

  def testUploadPassphraseWithServerError(self):
    self.mox.StubOutWithMock(base_client.time, 'sleep')
    self._UploadTest(500)
    base_client.time.sleep(mox.IsA(int))
    self._UploadTestReq(500)
    base_client.time.sleep(mox.IsA(int))
    self._UploadTestReq(500)
    base_client.time.sleep(mox.IsA(int))
    self._UploadTestReq(500)
    base_client.time.sleep(mox.IsA(int))
    self._UploadTestReq(500)

    self.mox.ReplayAll()
    self.assertRaises(
        base_client.RequestError,
        self.c.UploadPassphrase, 'foo', 'bar')
    self.mox.VerifyAll()




class BuildOauth2OpenerTest(mox.MoxTestBase):

  def testSuccess(self):
    creds = mox.MockAnything()
    creds.apply(mox.IsA(dict))
    self.mox.ReplayAll()
    opener = base_client.BuildOauth2Opener(creds)
    self.mox.VerifyAll()
    self.assertIsInstance(opener, urllib2.OpenerDirector)


if __name__ == '__main__':
  unittest.main()
