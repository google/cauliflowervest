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
# 
"""luks module tests."""



import mox
import stubout

from django.conf import settings
settings.configure()

from google.apputils import app
from google.apputils import basetest

from cauliflowervest import settings as base_settings
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import luks


class LuksRequestHandlerTest(mox.MoxTestBase):
  """Test the luks.Luks class."""

  def setUp(self):
    mox.MoxTestBase.setUp(self)
    self.c = luks.Luks()
    self.mox.StubOutWithMock(self.c, 'error')
    self.c.response = self.mox.CreateMockAnything()
    self.c.response.out = self.mox.CreateMockAnything()
    self.c.request = self.mox.CreateMockAnything()

  def tearDown(self):
    self.mox.UnsetStubs()

  def testVerifyEscrowTrailingSlash(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(luks.models.LuksVolume, 'get_by_key_name')

    volume_uuid = 'foovolumeuuid////'
    self.c.VerifyPermissions(permissions.ESCROW).AndReturn('user')
    luks.models.LuksVolume.get_by_key_name(volume_uuid.rstrip('/')).AndReturn(
        'anything')
    self.c.response.out.write('Escrow verified.')

    self.mox.ReplayAll()
    self.c.VerifyEscrow(volume_uuid)
    self.mox.VerifyAll()

  def testPutWithInvalidXsrfToken(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(util, 'XsrfTokenValidate')

    self.c.VerifyPermissions(permissions.ESCROW).AndReturn(None)
    self.c.request.get('xsrf-token', None).AndReturn('badtoken')
    util.XsrfTokenValidate('badtoken', 'UploadPassphrase').AndReturn(False)

    self.mox.ReplayAll()
    self.assertRaises(luks.models.AccessDeniedError, self.c.put, 'vol_uuid')
    self.mox.VerifyAll()

  def testPutWithMissingXsrfTokenAndProtectionDisabled(self):
    settings.XSRF_PROTECTION_ENABLED = False

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request.body = passphrase
    mock_user = self.mox.CreateMockAnything()
    mock_user.email = 'user@example.com'

    self.c.request.get('xsrf-token', None).AndReturn('token')
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.c.VerifyPermissions(permissions.ESCROW).AndReturn(mock_user)

    self.mox.StubOutWithMock(self.c, 'PutNewSecret')
    self.c.PutNewSecret(
        mock_user.email, volume_uuid, passphrase, self.c.request
        ).AndReturn(None)

    self.mox.ReplayAll()
    self.c.put(volume_uuid=volume_uuid)
    self.mox.VerifyAll()
    settings.XSRF_PROTECTION_ENABLED = True

  def testPutWithPassphrase(self):
    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request.body = passphrase

    mock_user = self.mox.CreateMockAnything()
    mock_user.email = 'user@example.com'
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.c.VerifyPermissions(permissions.ESCROW).AndReturn(mock_user)

    self.mox.StubOutWithMock(self.c, 'VerifyXsrfToken')
    self.c.VerifyXsrfToken(base_settings.SET_PASSPHRASE_ACTION)

    self.mox.StubOutWithMock(self.c, 'PutNewSecret')
    self.c.PutNewSecret(
        mock_user.email, volume_uuid, passphrase, self.c.request
        ).AndReturn(None)

    self.mox.ReplayAll()
    self.c.put(volume_uuid=volume_uuid)
    self.mox.VerifyAll()

  def testPutUnknown(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(luks.models.LuksAccessLog, 'Log')
    self.mox.StubOutWithMock(util, 'XsrfTokenValidate')

    self.c.VerifyPermissions(permissions.ESCROW).AndReturn(None)
    self.c.request.get('xsrf-token', None).AndReturn('token')
    util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)

    volume_uuid = 'foovolumeuuid'
    passphrase = ''
    self.c.request.body = passphrase

    luks.models.LuksAccessLog.Log(
        message='Unknown PUT', request=self.c.request)
    self.c.error(400).AndReturn(None)

    self.mox.ReplayAll()
    self.c.put(volume_uuid=volume_uuid)
    self.mox.VerifyAll()

  def testPutWithBrokenFormEncodedPassphrase(self):
    mock_user = self.mox.CreateMockAnything()
    mock_user.email = 'user@example.com'

    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.c.VerifyPermissions(permissions.ESCROW).AndReturn(mock_user)
    self.mox.StubOutWithMock(self.c, 'VerifyXsrfToken')
    self.c.VerifyXsrfToken(base_settings.SET_PASSPHRASE_ACTION)

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request = self.mox.CreateMockAnything()
    self.c.request.body = passphrase + '='

    self.mox.StubOutWithMock(self.c, 'PutNewSecret')
    self.c.PutNewSecret(
        mock_user.email, volume_uuid, passphrase, self.c.request
        ).AndReturn(None)

    self.mox.ReplayAll()
    self.c.put(volume_uuid)
    self.mox.VerifyAll()


def main(_):
  basetest.main()


if __name__ == '__main__':
  app.run()