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
# #

"""Tests for client module."""



import cookielib
import unittest

import mox
import stubout

from cauliflowervest.client import base_client


class CauliflowerVestClientTest(mox.MoxTestBase):
  """Test the base_client.CauliflowerVestClient class."""

  def setUp(self):
    super(CauliflowerVestClientTest, self).setUp()
    self.mox = mox.Mox()
    base_client.CauliflowerVestClient.ESCROW_PATH = 'foobar'
    self.c = base_client.CauliflowerVestClient('http://example.com')

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
    self.c.opener.open('request').AndReturn('200')

    self.mox.ReplayAll()
    ret = self.c._RetryRequest('request', 'foo desc')
    self.assertEqual(ret, '200')
    self.mox.VerifyAll()

  def testRetryRequest404(self):
    self.c.opener = self.mox.CreateMockAnything()
    mock_fp = self.mox.CreateMockAnything()
    err = base_client.urllib2.HTTPError('url', 404, 'HTTP Err 404', {}, mock_fp)
    self.c.opener.open('request').AndRaise(err)

    self.mox.ReplayAll()
    self.assertRaises(
        base_client.urllib2.HTTPError, self.c._RetryRequest, 'request', 'foo')
    self.mox.VerifyAll()

  def testRetryRequestRequestError(self):
    self.mox.StubOutWithMock(base_client.time, 'sleep')
    self.c.opener = self.mox.CreateMockAnything()
    mock_fp = self.mox.CreateMockAnything()
    err = base_client.urllib2.HTTPError('url', 500, 'HTTP Err 500', {}, mock_fp)

    self.c.opener.open('request').AndRaise(err)
    for i in xrange(0, self.c.MAX_TRIES - 1):
      base_client.time.sleep((i + 1) * self.c.TRY_DELAY_FACTOR)
      self.c.opener.open('request').AndRaise(err)

    self.mox.ReplayAll()
    self.assertRaises(
        base_client.RequestError, self.c._RetryRequest, 'request', 'foo')
    self.mox.VerifyAll()

  def testFetchXsrfToken(self):
    self.c.opener = self.mox.CreateMockAnything()
    mock_response = self.mox.CreateMockAnything()
    mock_response.read().AndReturn('mock-xsrf-token')
    self.c.opener.open(
        mox.IsA(base_client.fancy_urllib.FancyRequest)).AndReturn(mock_response)
    self.mox.ReplayAll()
    self.assertEquals('mock-xsrf-token', self.c._FetchXsrfToken('Action'))




if __name__ == '__main__':
  unittest.main()