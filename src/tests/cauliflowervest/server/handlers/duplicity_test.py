#!/usr/bin/env python
# 
# Copyright 2013 Google Inc. All Rights Reserved.
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
# """duplicity handler tests."""

import mox
import stubout

from django.conf import settings
settings.configure()

from google.appengine.api import users

# pylint: disable=g-bad-import-order
from google.apputils import app
from google.apputils import basetest

from cauliflowervest.server import util
from cauliflowervest.server.handlers import duplicity

VALID_UUID = 'ca7d099cb7a811e2b7a0ac162d075011'
INVALID_UUID = 'This is not a valid UUID, at all!'


class DuplicityRequestHandlerTest(mox.MoxTestBase):
  """Test the duplicity.Duplicity class."""

  def setUp(self):
    mox.MoxTestBase.setUp(self)
    self.c = duplicity.Duplicity()
    self.mox.StubOutWithMock(self.c, 'error')
    self.c.response = self.mox.CreateMockAnything()
    self.c.response.out = self.mox.CreateMockAnything()
    self.c.request = self.mox.CreateMockAnything()

    self.username = 'foouser@google.com'

    self.user = self.mox.CreateMock(users.User)
    self.user.email = lambda: self.username

    self.models_user = self.mox.CreateMockAnything()
    self.models_user.user = self.user
    self.models_user.email = self.user.email()

  def tearDown(self):
    self.mox.UnsetStubs()

  def testVerifyEscrow(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(
        duplicity.models.DuplicityKeyPair, 'get_by_key_name')

    self.c.VerifyPermissions(duplicity.permissions.ESCROW).AndReturn(None)
    duplicity.models.DuplicityKeyPair.get_by_key_name(VALID_UUID).AndReturn(
        'anything')
    self.c.response.out.write('Escrow verified.')

    self.mox.ReplayAll()
    self.c.VerifyEscrow(VALID_UUID)
    self.mox.VerifyAll()

  def testVerifyEscrow404(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(
        duplicity.models.DuplicityKeyPair, 'get_by_key_name')

    self.c.VerifyPermissions(duplicity.permissions.ESCROW).AndReturn(None)
    duplicity.models.DuplicityKeyPair.get_by_key_name(VALID_UUID).AndReturn(
        None)
    self.c.error(404).AndReturn(None)

    self.mox.ReplayAll()
    self.c.VerifyEscrow(VALID_UUID)
    self.mox.VerifyAll()

  def testGet(self):
    self.mox.StubOutWithMock(self.c, 'RetrieveSecret')
    self.c.request.get('only_verify_escrow').AndReturn('')
    self.c.RetrieveSecret(VALID_UUID).AndReturn(None)
    self.mox.ReplayAll()
    self.c.get(volume_uuid=VALID_UUID)
    self.mox.VerifyAll()

  def testGetWithOnlyVerify(self):
    self.mox.StubOutWithMock(self.c, 'VerifyEscrow')
    self.c.request.get('only_verify_escrow').AndReturn('1')
    self.c.VerifyEscrow(VALID_UUID).AndReturn(None)
    self.mox.ReplayAll()
    self.c.get(volume_uuid=VALID_UUID)
    self.mox.VerifyAll()

  def testGetWithoutVolumeUUID(self):
    self.mox.StubOutWithMock(self.c, 'VerifyEscrow')
    self.mox.ReplayAll()
    self.assertRaises(duplicity.models.DuplicityAccessError, self.c.get)
    self.mox.VerifyAll()

  def testPutWithInvalidXsrfToken(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(util, 'XsrfTokenValidate')

    self.c.VerifyPermissions(duplicity.permissions.ESCROW).AndReturn(
        self.models_user)
    self.c.request.get('xsrf-token', None).AndReturn('badtoken')
    util.XsrfTokenValidate('badtoken', 'UploadPassphrase').AndReturn(False)

    self.mox.ReplayAll()
    self.assertRaises(duplicity.models.AccessDeniedError,
                      self.c.put, 'vol_uuid')
    self.mox.VerifyAll()

  def testPutWithKeyPair(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(self.c, 'PutNewKeyPair')
    self.mox.StubOutWithMock(util, 'XsrfTokenValidate')

    key_pair = 'fookey_pair'
    self.c.request.body = key_pair

    self.c.VerifyPermissions(duplicity.permissions.ESCROW).AndReturn(
        self.models_user)
    self.c.request.get('xsrf-token', None).AndReturn('token')
    util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)
    self.c.PutNewKeyPair(
        self.username, VALID_UUID, key_pair, self.c.request).AndReturn(None)

    self.mox.ReplayAll()
    self.c.put(volume_uuid=VALID_UUID)
    self.mox.VerifyAll()

  def testPutUnknown(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(duplicity.models.DuplicityAccessLog, 'Log')
    self.mox.StubOutWithMock(util, 'XsrfTokenValidate')

    self.c.VerifyPermissions(duplicity.permissions.ESCROW).AndReturn(
        self.models_user)
    self.c.request.get('xsrf-token', None).AndReturn('token')
    util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)

    key_pair = ''
    self.c.request.body = key_pair

    duplicity.models.DuplicityAccessLog.Log(
        message='Unknown PUT', request=self.c.request)
    self.c.error(400).AndReturn(None)

    self.mox.ReplayAll()
    self.c.put(volume_uuid=VALID_UUID)
    self.mox.VerifyAll()

  def testPutWithBrokenFormEncodedKeyPair(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(self.c, 'PutNewKeyPair')
    self.mox.StubOutWithMock(util, 'XsrfTokenValidate')
    self.mox.StubOutWithMock(duplicity.models.DuplicityAccessLog, 'Log')

    key_pair = 'fookey_pair'

    self.c.request.body = key_pair + '='
    self.c.VerifyPermissions(duplicity.permissions.ESCROW).AndReturn(
        self.models_user)
    self.c.request.get('xsrf-token', None).AndReturn('token')
    util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)
    self.c.PutNewKeyPair(self.username, VALID_UUID, key_pair, mox.IgnoreArg())
    self.mox.ReplayAll()

    self.c.put(VALID_UUID)
    self.mox.VerifyAll()

  def testPutNewKeyPair(self):
    self.mox.StubOutWithMock(duplicity.models, 'DuplicityKeyPair')
    self.mox.StubOutWithMock(duplicity.models.DuplicityAccessLog, 'Log')

    key_pair = 'key_pair'
    metadata = {
        'owner': self.username,
        'hostname': 'anything',
        'etc': 'anything'
        }

    mock_entity = self.mox.CreateMockAnything()
    duplicity.models.DuplicityKeyPair(
        key_name=VALID_UUID,
        volume_uuid=VALID_UUID,
        key_pair=key_pair,
        owner=self.username).AndReturn(mock_entity)
    mock_entity.properties().AndReturn(metadata.keys())

    mock_entity.put().AndReturn(None)

    duplicity.models.DuplicityAccessLog.Log(
        entity=mock_entity, message='PUT', request=self.c.request)

    self.c.response.out.write('Key pair successfully escrowed!')

    self.mox.ReplayAll()
    self.c.PutNewKeyPair(self.username, VALID_UUID, key_pair, metadata)
    self.mox.VerifyAll()


def main(_):
  basetest.main()


if __name__ == '__main__':
  app.run()