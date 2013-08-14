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

"""filevault module tests."""



import mox
import stubout

from django.conf import settings
settings.configure()

# pylint: disable=g-bad-import-order
import webapp2
from google.appengine.api import users
from google.appengine.ext import testbed

from google.apputils import app
from google.apputils import basetest

from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import filevault as fv


class FileVaultRequestHandlerTest(mox.MoxTestBase):
  """Test the filevault.FileVault class."""

  def setUp(self):
    mox.MoxTestBase.setUp(self)
    self.c = fv.FileVault()
    self.mox.StubOutWithMock(self.c, 'error')
    self.c.response = self.mox.CreateMockAnything()
    self.c.response.out = self.mox.CreateMockAnything()
    self.c.request = self.mox.CreateMockAnything()

  def tearDown(self):
    self.mox.UnsetStubs()

  def testPutWithInvalidXsrfToken(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(fv.util, 'XsrfTokenValidate')

    self.c.VerifyPermissions(fv.permissions.ESCROW).AndReturn(None)
    self.c.request.get('xsrf-token', None).AndReturn('badtoken')
    fv.util.XsrfTokenValidate('badtoken', 'UploadPassphrase').AndReturn(False)

    self.mox.ReplayAll()
    self.assertRaises(fv.models.AccessDeniedError, self.c.put, 'vol_uuid')
    self.mox.VerifyAll()

  def testPutWithMissingXsrfTokenAndProtectionDisabled(self):
    self.mox.StubOutWithMock(self.c, 'IsValidUuid')
    self.mox.StubOutWithMock(self.c, 'PutNewPassphrase')
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')

    settings.XSRF_PROTECTION_ENABLED = False
    self.c.VerifyPermissions(fv.permissions.ESCROW).AndReturn(None)

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request.body = passphrase

    self.c.request.get('xsrf-token', None).AndReturn(None)
    self.c.IsValidUuid(volume_uuid).AndReturn(True)
    self.c.IsValidUuid(passphrase).AndReturn(True)
    self.c.PutNewPassphrase(volume_uuid, passphrase, self.c.request).AndReturn(
        None)

    self.mox.ReplayAll()
    self.c.put(volume_uuid=volume_uuid)
    self.mox.VerifyAll()
    settings.XSRF_PROTECTION_ENABLED = True

  def testPutWithPassphrase(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(self.c, 'PutNewPassphrase')
    self.mox.StubOutWithMock(self.c, 'IsValidUuid')
    self.mox.StubOutWithMock(fv.util, 'XsrfTokenValidate')

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request.body = passphrase

    self.c.VerifyPermissions(fv.permissions.ESCROW).AndReturn(None)
    self.c.request.get('xsrf-token', None).AndReturn('token')
    fv.util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)
    self.c.IsValidUuid(volume_uuid).AndReturn(True)
    self.c.IsValidUuid(passphrase).AndReturn(True)
    self.c.PutNewPassphrase(volume_uuid, passphrase, self.c.request).AndReturn(
        None)

    self.mox.ReplayAll()
    self.c.put(volume_uuid=volume_uuid)
    self.mox.VerifyAll()

  def testPutUnknown(self):
    self.mox.StubOutWithMock(self.c, 'IsValidUuid')
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(fv.models.FileVaultAccessLog, 'Log')
    self.mox.StubOutWithMock(fv.util, 'XsrfTokenValidate')

    self.c.VerifyPermissions(fv.permissions.ESCROW).AndReturn(None)
    self.c.request.get('xsrf-token', None).AndReturn('token')
    fv.util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)

    volume_uuid = 'foovolumeuuid'
    passphrase = ''
    self.c.request.body = passphrase

    fv.models.FileVaultAccessLog.Log(
        message='Unknown PUT', request=self.c.request)
    self.c.error(400).AndReturn(None)

    self.mox.ReplayAll()
    self.c.put(volume_uuid=volume_uuid)
    self.mox.VerifyAll()

  def testPutWithInvalidVolumeUUID(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(self.c, 'IsValidUuid')
    self.mox.StubOutWithMock(fv.util, 'XsrfTokenValidate')

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request.body = passphrase

    self.c.VerifyPermissions(fv.permissions.ESCROW).AndReturn(None)
    self.c.request.get('xsrf-token', None).AndReturn('token')
    fv.util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)
    self.c.IsValidUuid(volume_uuid).AndReturn(False)

    self.mox.ReplayAll()
    self.assertRaises(fv.models.FileVaultAccessError, self.c.put, volume_uuid)
    self.mox.VerifyAll()

  def testPutWithBrokenFormEncodedPassphrase(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(self.c, 'IsValidUuid')
    self.mox.StubOutWithMock(fv.util, 'XsrfTokenValidate')

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request.body = passphrase + '='

    self.c.VerifyPermissions(fv.permissions.ESCROW).AndReturn(None)
    self.c.request.get('xsrf-token', None).AndReturn('token')
    fv.util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)
    self.c.IsValidUuid(volume_uuid).AndReturn(True)
    self.c.IsValidUuid(passphrase).AndReturn(False)

    self.mox.ReplayAll()
    self.assertRaises(fv.models.FileVaultAccessError, self.c.put, volume_uuid)
    self.mox.VerifyAll()

  def testPutWithInvalidPassphrase(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(self.c, 'IsValidUuid')
    self.mox.StubOutWithMock(fv.util, 'XsrfTokenValidate')

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request.body = passphrase

    self.c.VerifyPermissions(fv.permissions.ESCROW).AndReturn(None)
    self.c.request.get('xsrf-token', None).AndReturn('token')
    fv.util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)
    self.c.IsValidUuid(volume_uuid).AndReturn(True)
    self.c.IsValidUuid(passphrase).AndReturn(False)

    self.mox.ReplayAll()
    self.assertRaises(fv.models.FileVaultAccessError, self.c.put, volume_uuid)
    self.mox.VerifyAll()

  def testPutNewPassphraseWithEmptyVolumeUUID(self):
    self.mox.StubOutWithMock(fv.models, 'FileVaultVolume')

    self.mox.ReplayAll()
    self.assertRaises(
        fv.models.FileVaultAccessError, self.c.PutNewPassphrase, None, 'f', {})
    self.mox.VerifyAll()

  def testPutNewPassphrase(self):
    self.mox.StubOutWithMock(fv.models, 'FileVaultVolume')
    self.mox.StubOutWithMock(fv.models.FileVaultAccessLog, 'Log')

    metadata = {'owner': 'anything', 'hostname': 'anything', 'etc': 'anything'}
    volume_uuid = 'foovolumeuuid'
    passphrase = 'passphrase'
    mock_entity = self.mox.CreateMockAnything()
    fv.models.FileVaultVolume(
        key_name=volume_uuid,
        volume_uuid=volume_uuid,
        passphrase=passphrase).AndReturn(mock_entity)
    mock_entity.properties().AndReturn(metadata.keys())

    mock_entity.put().AndReturn(None)

    fv.models.FileVaultAccessLog.Log(
        entity=mock_entity, message='PUT', request=self.c.request)

    self.c.response.out.write('Passphrase successfully escrowed!')

    self.mox.ReplayAll()
    self.c.PutNewPassphrase(volume_uuid, passphrase, metadata)
    self.mox.VerifyAll()




def main(_):
  basetest.main()


if __name__ == '__main__':
  app.run()