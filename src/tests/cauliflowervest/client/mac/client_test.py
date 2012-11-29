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



import unittest

import mox
import stubout

from cauliflowervest.client.mac import client


class FileVaultClientTest(mox.MoxTestBase):
  """Test the client.FileVaultClient class."""

  def setUp(self):
    super(FileVaultClientTest, self).setUp()
    self.mox = mox.Mox()
    self.url = 'http://localhost:8080'
    self.mock_opener = self.mox.CreateMockAnything()
    self.c = client.FileVaultClient(self.url, self.mock_opener)

  def tearDown(self):
    self.mox.UnsetStubs()

  def _RetrieveTest(self, code, read=True):
    self.volume_uuid = 'foostrvolumeuuid'
    self.passphrase = 'foopassphrase'
    content = '{"passphrase": "%s"}' % self.passphrase

    self.mox.StubOutWithMock(self.c, '_FetchXsrfToken')
    self.c._FetchXsrfToken('RetrievePassphrase').AndReturn('token')

    if code == 200:
      mock_response = self.mox.CreateMockAnything()
      self.mock_opener.open(
          mox.IsA(client.base_client.fancy_urllib.FancyRequest)).AndReturn(
              mock_response)
      mock_response.code = code
      if read:
        mock_response.read().AndReturn(client.JSON_PREFIX + content)
    else:
      mock_fp = self.mox.CreateMockAnything()
      exc = client.urllib2.HTTPError(
          'url', code, 'HTTP Error %s' % code, {}, mock_fp)
      self.mock_opener.open(
          mox.IsA(client.base_client.fancy_urllib.FancyRequest)).AndRaise(exc)

  def testRetrievePassphrase(self):
    self._RetrieveTest(200)
    self.mox.ReplayAll()
    ret = self.c.RetrievePassphrase('foo')
    self.assertEqual(ret, self.passphrase)
    self.mox.VerifyAll()

  def testRetrievePassphraseRequestError(self):
    self._RetrieveTest(403)
    self.mox.ReplayAll()
    self.assertRaises(
        client.RequestError,
        self.c.RetrievePassphrase, self.volume_uuid)
    self.mox.VerifyAll()

  def _UploadTest(self, code):
    self.mox.StubOutWithMock(self.c, 'GetAndValidateMetadata')
    self.mox.StubOutWithMock(self.c, '_FetchXsrfToken')

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
          mox.IsA(client.base_client.fancy_urllib.FancyRequest)).AndReturn(
              mock_response)
    else:
      mock_fp = self.mox.CreateMockAnything()
      exc = client.urllib2.HTTPError(
          'url', code, 'HTTP Error %s' % code, {}, mock_fp)
      self.mock_opener.open(
          mox.IsA(client.base_client.fancy_urllib.FancyRequest)).AndRaise(exc)

  def testUploadPassphrase(self):
    self._UploadTest(200)
    self.mox.ReplayAll()
    self.c.UploadPassphrase('foo', 'bar')
    self.mox.VerifyAll()

  def testUploadPassphraseWithTransientRequestError(self):
    self.mox.StubOutWithMock(client.base_client.time, 'sleep')
    self._UploadTest(500)
    client.base_client.time.sleep(mox.IsA(int))
    self._UploadTestReq(500)
    client.base_client.time.sleep(mox.IsA(int))
    self._UploadTestReq(200)

    self.mox.ReplayAll()
    self.c.UploadPassphrase('foo', 'bar')
    self.mox.VerifyAll()

  def testUploadPassphraseWithRequestError(self):
    self.mox.StubOutWithMock(client.base_client.time, 'sleep')
    self._UploadTest(403)
    client.base_client.time.sleep(mox.IsA(int))
    self._UploadTestReq(403)
    client.base_client.time.sleep(mox.IsA(int))
    self._UploadTestReq(403)
    client.base_client.time.sleep(mox.IsA(int))
    self._UploadTestReq(403)
    client.base_client.time.sleep(mox.IsA(int))
    self._UploadTestReq(403)

    self.mox.ReplayAll()
    self.assertRaises(
        client.RequestError,
        self.c.UploadPassphrase, 'foo', 'bar')
    self.mox.VerifyAll()


if __name__ == '__main__':
  unittest.main()