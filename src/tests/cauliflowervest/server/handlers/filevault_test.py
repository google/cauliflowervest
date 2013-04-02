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

from google.appengine.api import users  # pylint: disable-msg=C6203

from google.apputils import app
from google.apputils import basetest

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

  def testRetrievePassphraseWithInvalidVolumeUUID(self):
    self.mox.StubOutWithMock(self.c, 'VerifyXsrfToken')
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(fv.models.FileVaultVolume, 'get_by_key_name')

    self.c.VerifyXsrfToken('RetrievePassphrase')
    self.c.VerifyPermissions(fv.permissions.RETRIEVE).AndReturn('user')
    volume_uuid = 'does-not-exist'
    fv.models.FileVaultVolume.get_by_key_name(volume_uuid).AndReturn(None)

    self.mox.ReplayAll()
    self.assertRaises(
        fv.models.FileVaultAccessError, self.c.RetrievePassphrase, volume_uuid)
    self.mox.VerifyAll()

  def testRetrievePassphrase(self):
    self.mox.StubOutWithMock(self.c, 'VerifyXsrfToken')
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(self.c, 'SendRetrievalEmail')
    self.mox.StubOutWithMock(fv.models.FileVaultAccessLog, 'Log')
    self.mox.StubOutWithMock(fv.models.FileVaultVolume, 'get_by_key_name')

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    mock_entity = self.mox.CreateMockAnything()
    mock_entity.passphrase = passphrase

    self.c.VerifyXsrfToken('RetrievePassphrase')
    self.c.VerifyPermissions(fv.permissions.RETRIEVE).AndReturn('user')
    fv.models.FileVaultVolume.get_by_key_name(volume_uuid).AndReturn(
        mock_entity)

    fv.models.FileVaultAccessLog.Log(
        message='GET', entity=mock_entity, request=self.c.request)

    self.c.SendRetrievalEmail(mock_entity, 'user').AndReturn(None)
    self.c.request.get('json', '1').AndReturn('1')
    self.c.response.out.write(
        fv.JSON_PREFIX + '{"passphrase": "%s"}' % passphrase)

    self.mox.ReplayAll()
    self.c.RetrievePassphrase(volume_uuid)
    self.mox.VerifyAll()

# TODO(user): Uncomment these lines after the special case is removed
# on 2012/12/01.
# def testRetrievePassphraseWithMissingXsrfToken(self):
#   self.c.request.get('xsrf-token', None).AndReturn(None)
#   self.c.request.get('json', '1').AndReturn('1')

#   self.mox.ReplayAll()
#   self.assertRaises(fv.models.AccessDeniedError, self.c.RetrievePassphrase,
#                     'foovolumeuuid')
#   self.mox.VerifyAll()

# def testRetrievePassphraseWithInvalidXsrfToken(self):
#   self.mox.StubOutWithMock(fv.util, 'XsrfTokenValidate')

#   invalid_token = 'foo'
#   self.c.request.get('xsrf-token', None).AndReturn(invalid_token)
#   self.c.request.get('json', '1').AndReturn('1')
#   fv.util.XsrfTokenValidate(
#       invalid_token, 'RetrievePassphrase').AndReturn(False)

#   self.mox.ReplayAll()
#   self.assertRaises(fv.models.AccessDeniedError, self.c.RetrievePassphrase,
#                     'foovolumeuuid')
#   self.mox.VerifyAll()

  def testVerifyEscrow(self):
    self.mox.StubOutWithMock(self.c, 'VerifyDomainUser')
    self.mox.StubOutWithMock(fv.models.FileVaultVolume, 'get_by_key_name')

    volume_uuid = 'foovolumeuuid'
    self.c.VerifyDomainUser().AndReturn(None)
    fv.models.FileVaultVolume.get_by_key_name(volume_uuid).AndReturn('anything')
    self.c.response.out.write('Escrow verified.')

    self.mox.ReplayAll()
    self.c.VerifyEscrow(volume_uuid)
    self.mox.VerifyAll()

  def testVerifyEscrow404(self):
    self.mox.StubOutWithMock(self.c, 'VerifyDomainUser')
    self.mox.StubOutWithMock(fv.models.FileVaultVolume, 'get_by_key_name')

    volume_uuid = 'foovolumeuuid'
    self.c.VerifyDomainUser().AndReturn(None)
    fv.models.FileVaultVolume.get_by_key_name(volume_uuid).AndReturn(None)
    self.c.error(404).AndReturn(None)

    self.mox.ReplayAll()
    self.c.VerifyEscrow(volume_uuid)
    self.mox.VerifyAll()

  def testGet(self):
    self.mox.StubOutWithMock(self.c, 'RetrievePassphrase')
    self.mox.StubOutWithMock(self.c, 'IsSaneUuid')
    volume_uuid = 'foovolumeuuid'
    self.c.IsSaneUuid(volume_uuid).AndReturn(True)
    self.c.request.get('only_verify_escrow').AndReturn('')
    self.c.RetrievePassphrase(volume_uuid).AndReturn(None)
    self.mox.ReplayAll()
    self.c.get(volume_uuid=volume_uuid)
    self.mox.VerifyAll()

  def testGetWithOnlyVerify(self):
    self.mox.StubOutWithMock(self.c, 'VerifyEscrow')
    self.mox.StubOutWithMock(self.c, 'IsSaneUuid')
    volume_uuid = 'foovolumeuuid'
    self.c.IsSaneUuid(volume_uuid).AndReturn(True)
    self.c.request.get('only_verify_escrow').AndReturn('1')
    self.c.VerifyEscrow(volume_uuid).AndReturn(None)
    self.mox.ReplayAll()
    self.c.get(volume_uuid=volume_uuid)
    self.mox.VerifyAll()

  def testGetWithoutVolumeUUID(self):
    self.mox.StubOutWithMock(self.c, 'VerifyEscrow')
    self.mox.ReplayAll()
    self.assertRaises(fv.models.FileVaultAccessError, self.c.get)
    self.mox.VerifyAll()

  def testGetWithoutInsaneVolumeUUID(self):
    self.mox.StubOutWithMock(self.c, 'VerifyEscrow')
    self.mox.StubOutWithMock(self.c, 'IsSaneUuid')
    volume_uuid = 'foovolumeuuid'
    self.c.IsSaneUuid(volume_uuid).AndReturn(False)
    self.mox.ReplayAll()
    self.assertRaises(fv.models.FileVaultAccessError, self.c.get, volume_uuid)
    self.mox.VerifyAll()

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
    self.mox.StubOutWithMock(self.c, 'IsSaneUuid')
    self.mox.StubOutWithMock(self.c, 'PutNewPassphrase')
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')

    fv.settings.XSRF_PROTECTION_ENABLED = False
    self.c.VerifyPermissions(fv.permissions.ESCROW).AndReturn(None)

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request.body = passphrase

    self.c.request.get('xsrf-token', None).AndReturn(None)
    self.c.IsSaneUuid(volume_uuid).AndReturn(True)
    self.c.IsSaneUuid(passphrase).AndReturn(True)
    self.c.PutNewPassphrase(volume_uuid, passphrase, self.c.request).AndReturn(
        None)

    self.mox.ReplayAll()
    self.c.put(volume_uuid=volume_uuid)
    self.mox.VerifyAll()
    fv.settings.XSRF_PROTECTION_ENABLED = True

  def testPutWithPassphraseWithAllDomainUsersOn(self):
    self.mox.StubOutWithMock(self.c, 'VerifyDomainUser')
    self.mox.StubOutWithMock(self.c, 'PutNewPassphrase')
    self.mox.StubOutWithMock(self.c, 'IsSaneUuid')
    self.mox.StubOutWithMock(fv.util, 'XsrfTokenValidate')

    self.c.VerifyDomainUser().AndReturn('foouser')
    self.c.request.get('xsrf-token', None).AndReturn('token')
    fv.util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request.body = passphrase

    self.c.IsSaneUuid(volume_uuid).AndReturn(True)
    self.c.IsSaneUuid(passphrase).AndReturn(True)
    self.c.PutNewPassphrase(volume_uuid, passphrase, self.c.request).AndReturn(
        None)

    fv.settings.ALLOW_ALL_DOMAIN_USERS_TO_ESCROW = True
    self.mox.ReplayAll()
    self.c.put(volume_uuid=volume_uuid)
    self.mox.VerifyAll()

  def testPutUnknownWithAllDomainUsersOn(self):
    self.mox.StubOutWithMock(self.c, 'IsSaneUuid')
    self.mox.StubOutWithMock(self.c, 'VerifyDomainUser')
    self.mox.StubOutWithMock(fv.models.FileVaultAccessLog, 'Log')
    self.mox.StubOutWithMock(fv.util, 'XsrfTokenValidate')

    self.c.VerifyDomainUser().AndReturn('foouser')
    self.c.request.get('xsrf-token', None).AndReturn('token')
    fv.util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)

    volume_uuid = 'foovolumeuuid'
    passphrase = ''
    self.c.request.body = passphrase

    fv.models.FileVaultAccessLog.Log(
        message='Unknown PUT', request=self.c.request)
    self.c.error(400).AndReturn(None)

    fv.settings.ALLOW_ALL_DOMAIN_USERS_TO_ESCROW = True
    self.mox.ReplayAll()
    self.c.put(volume_uuid=volume_uuid)
    self.mox.VerifyAll()

  def testPutWithPassphraseWithAllDomainUsersOff(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(self.c, 'PutNewPassphrase')
    self.mox.StubOutWithMock(self.c, 'IsSaneUuid')
    self.mox.StubOutWithMock(fv.util, 'XsrfTokenValidate')

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request.body = passphrase

    self.c.VerifyPermissions(fv.permissions.ESCROW).AndReturn(None)
    self.c.request.get('xsrf-token', None).AndReturn('token')
    fv.util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)
    self.c.IsSaneUuid(volume_uuid).AndReturn(True)
    self.c.IsSaneUuid(passphrase).AndReturn(True)
    self.c.PutNewPassphrase(volume_uuid, passphrase, self.c.request).AndReturn(
        None)

    fv.settings.ALLOW_ALL_DOMAIN_USERS_TO_ESCROW = False
    self.mox.ReplayAll()
    self.c.put(volume_uuid=volume_uuid)
    self.mox.VerifyAll()

  def testPutUnknownWithAllDomainUsersOff(self):
    self.mox.StubOutWithMock(self.c, 'IsSaneUuid')
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

    fv.settings.ALLOW_ALL_DOMAIN_USERS_TO_ESCROW = False
    self.mox.ReplayAll()
    self.c.put(volume_uuid=volume_uuid)
    self.mox.VerifyAll()

  def testPutWithInsaneVolumeUUID(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(self.c, 'IsSaneUuid')
    self.mox.StubOutWithMock(fv.util, 'XsrfTokenValidate')

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request.body = passphrase

    self.c.VerifyPermissions(fv.permissions.ESCROW).AndReturn(None)
    self.c.request.get('xsrf-token', None).AndReturn('token')
    fv.util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)
    self.c.IsSaneUuid(volume_uuid).AndReturn(False)

    fv.settings.ALLOW_ALL_DOMAIN_USERS_TO_ESCROW = False
    self.mox.ReplayAll()
    self.assertRaises(fv.models.FileVaultAccessError, self.c.put, volume_uuid)
    self.mox.VerifyAll()

  def testPutWithBrokenFormEncodedPassphrase(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(self.c, 'IsSaneUuid')
    self.mox.StubOutWithMock(fv.util, 'XsrfTokenValidate')

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request.body = passphrase + '='

    self.c.VerifyPermissions(fv.permissions.ESCROW).AndReturn(None)
    self.c.request.get('xsrf-token', None).AndReturn('token')
    fv.util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)
    self.c.IsSaneUuid(volume_uuid).AndReturn(True)
    self.c.IsSaneUuid(passphrase).AndReturn(False)

    fv.settings.ALLOW_ALL_DOMAIN_USERS_TO_ESCROW = False
    self.mox.ReplayAll()
    self.assertRaises(fv.models.FileVaultAccessError, self.c.put, volume_uuid)
    self.mox.VerifyAll()

  def testPutWithInsanePassphrase(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(self.c, 'IsSaneUuid')
    self.mox.StubOutWithMock(fv.util, 'XsrfTokenValidate')

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    self.c.request.body = passphrase

    self.c.VerifyPermissions(fv.permissions.ESCROW).AndReturn(None)
    self.c.request.get('xsrf-token', None).AndReturn('token')
    fv.util.XsrfTokenValidate('token', 'UploadPassphrase').AndReturn(True)
    self.c.IsSaneUuid(volume_uuid).AndReturn(True)
    self.c.IsSaneUuid(passphrase).AndReturn(False)

    fv.settings.ALLOW_ALL_DOMAIN_USERS_TO_ESCROW = False
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

  def testSendRetrievalEmailByPermListUser(self):
    mock_user = self.mox.CreateMockAnything(fv.models.User)
    mock_user.user = self.mox.CreateMockAnything(users.User)
    mock_user.user.email = lambda: 'mock_user@example.com'
    mock_entity = self.mox.CreateMockAnything(fv.models.FileVaultVolume)
    mock_entity.owner = 'mock_owner@example.com'
    self.mox.StubOutWithMock(fv.util, 'SendEmail')
    self.mox.StubOutWithMock(fv.settings, 'RETRIEVE_AUDIT_ADDRESSES')
    fv.settings.RETRIEVE_AUDIT_ADDRESSES = ['mock_email2@example.com']
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')

    self.c.VerifyPermissions(fv.permissions.SILENT_RETRIEVE, mock_user)
    fv.util.SendEmail(
        [mock_user.user.email()] + fv.settings.SILENT_AUDIT_ADDRESSES,
        mox.IsA(basestring), mox.IsA(basestring))
    self.mox.ReplayAll()
    self.c.SendRetrievalEmail(mock_entity, mock_user)
    self.mox.VerifyAll()

  def testSendRetrievalEmailByPermReadUser(self):
    mock_user = self.mox.CreateMockAnything(fv.models.User)
    mock_user.user = self.mox.CreateMockAnything(users.User)
    mock_user.user.email = lambda: 'mock_user@example.com'
    mock_entity = self.mox.CreateMockAnything(fv.models.FileVaultVolume)
    mock_entity.owner = 'mock_owner'
    self.mox.StubOutWithMock(fv.util, 'SendEmail')
    self.mox.StubOutWithMock(fv.settings, 'RETRIEVE_AUDIT_ADDRESSES')
    fv.settings.RETRIEVE_AUDIT_ADDRESSES = ['mock_email2@example.com']
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')

    self.c.VerifyPermissions(
        fv.permissions.SILENT_RETRIEVE, mock_user).AndRaise(
            fv.models.FileVaultAccessDeniedError('test'))
    owner_email = '%s@%s' % (
        mock_entity.owner, fv.settings.DEFAULT_EMAIL_DOMAIN)
    user_email = mock_user.user.email()
    fv.util.SendEmail(
        [owner_email, user_email] + fv.settings.RETRIEVE_AUDIT_ADDRESSES,
        mox.IsA(basestring), mox.IsA(basestring))
    self.mox.ReplayAll()
    self.c.SendRetrievalEmail(mock_entity, mock_user)
    self.mox.VerifyAll()


def main(_):
  basetest.main()


if __name__ == '__main__':
  app.run()
