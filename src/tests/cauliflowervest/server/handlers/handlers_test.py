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
# #

"""handlers module tests."""

import mox
import stubout

from django.conf import settings
settings.configure()

# pylint: disable=g-bad-import-order
from google.appengine.api import users
from google.appengine.ext import testbed

from google.apputils import app
from google.apputils import basetest

from cauliflowervest.server import handlers
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util


class GetTest(mox.MoxTestBase):

  def setUp(self):
    super(GetTest, self).setUp()

    self.testbed = testbed.Testbed()
    self.testbed.activate()

    self.c = handlers.LuksAccessHandler()

  def tearDown(self):
    super(GetTest, self).tearDown()
    self.testbed.deactivate()

  def testInvalidVolumeUUID(self):
    self.mox.StubOutWithMock(self.c, 'VerifyEscrow')
    self.mox.StubOutWithMock(self.c, 'IsValidUuid')
    volume_uuid = 'foovolumeuuid'
    self.c.IsValidUuid(volume_uuid).AndReturn(False)
    self.mox.ReplayAll()
    self.assertRaises(models.AccessError, self.c.get, volume_uuid)
    self.mox.VerifyAll()

  def testNominal(self):
    self.mox.StubOutWithMock(self.c, 'RetrieveSecret')
    volume_uuid = 'foovolumeuuid'
    self.c.request = {'only_verify_escrow': ''}
    self.c.RetrieveSecret(volume_uuid).AndReturn(None)
    self.mox.ReplayAll()
    self.c.get(volume_uuid=volume_uuid)
    self.mox.VerifyAll()

  def testOnlyVerify(self):
    self.mox.StubOutWithMock(self.c, 'VerifyEscrow')
    volume_uuid = 'foovolumeuuid'
    self.c.request = {'only_verify_escrow': '1'}
    self.c.VerifyEscrow(volume_uuid)
    self.mox.ReplayAll()
    self.c.get(volume_uuid=volume_uuid)
    self.mox.VerifyAll()

  def testWithoutVolumeUUID(self):
    self.mox.StubOutWithMock(self.c, 'VerifyEscrow')
    self.mox.ReplayAll()
    self.assertRaises(models.AccessError, self.c.get)
    self.mox.VerifyAll()


class PutNewSecretTest(mox.MoxTestBase):

  def setUp(self):
    super(PutNewSecretTest, self).setUp()
    self.c = handlers.LuksAccessHandler()
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()

  def testEmptyVolumeUuid(self):
    self.mox.StubOutWithMock(models, 'LuksVolume')

    self.mox.ReplayAll()
    self.assertRaises(
        models.AccessError,
        self.c.PutNewSecret, 'owner', None, 'f', {})
    self.mox.VerifyAll()

  def testNominal(self):
    self.mox.StubOutWithMock(models.LuksAccessLog, 'Log')

    metadata = {
        'etc': 'anything',
        'hdd_serial': 'anything',
        'hostname': 'anything',
        'owner': 'anything',
        'platform_uuid': 'anything',
        }
    volume_uuid = 'foovolumeuuid'
    passphrase = 'passphrase'

    self.mox.StubOutWithMock(self.c, '_CreateNewSecretEntity')
    mock_entity = models.LuksVolume(
        key_name=volume_uuid,
        volume_uuid=volume_uuid,
        passphrase=passphrase)
    self.c._CreateNewSecretEntity(
        'owner', volume_uuid, passphrase
        ).AndReturn(mock_entity)
    self.mox.StubOutWithMock(mock_entity, 'put')
    mock_entity.put()

    models.LuksAccessLog.Log(
        entity=mock_entity, message='PUT', request=self.c.request)

    self.c.response = self.mox.CreateMockAnything()
    self.c.response.out = self.mox.CreateMockAnything()
    self.c.response.out.write(mox.IsA(basestring))


    self.mox.ReplayAll()
    self.c.PutNewSecret('owner', volume_uuid, passphrase, metadata)
    self.mox.VerifyAll()


class RetrieveSecretTest(mox.MoxTestBase):

  def setUp(self):
    super(RetrieveSecretTest, self).setUp()

    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

    self.c = handlers.LuksAccessHandler()

  def tearDown(self):
    super(RetrieveSecretTest, self).tearDown()
    self.testbed.deactivate()

  def testAsNonOwner(self):
    self.mox.StubOutWithMock(self.c, 'VerifyXsrfToken')
    self.c.VerifyXsrfToken('RetrieveSecret')

    mock_user = self.mox.CreateMockAnything()
    mock_user.email = 'mock_user_bar@example.com'
    self.mox.StubOutWithMock(models, 'GetCurrentUser')
    models.GetCurrentUser().AndReturn(mock_user)

    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.c.VerifyPermissions(
        permissions.RETRIEVE, user=mock_user
        ).AndRaise(models.AccessDeniedError('user is not an admin'))
    self.c.VerifyPermissions(
        permissions.RETRIEVE_OWN, user=mock_user
        )

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    mock_entity = self.mox.CreateMockAnything()
    mock_entity.passphrase = passphrase
    mock_entity.owner = 'mock_user_foo@example.com'

    self.mox.StubOutWithMock(models.LuksVolume, 'get_by_key_name')
    models.LuksVolume.get_by_key_name(volume_uuid).AndReturn(mock_entity)

    self.mox.ReplayAll()
    self.assertRaises(
        models.AccessError,
        self.c.RetrieveSecret, volume_uuid)
    self.mox.VerifyAll()

  def testAsOwner(self):
    self.mox.StubOutWithMock(self.c, 'VerifyXsrfToken')
    self.c.VerifyXsrfToken('RetrieveSecret')

    mock_user = self.mox.CreateMockAnything()
    mock_user.email = 'mock_user_foo@example.com'
    self.mox.StubOutWithMock(models, 'GetCurrentUser')
    models.GetCurrentUser().AndReturn(mock_user)

    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.c.VerifyPermissions(
        permissions.RETRIEVE, user=mock_user
        ).AndRaise(models.AccessDeniedError('user is not an admin'))
    self.c.VerifyPermissions(
        permissions.RETRIEVE_OWN, user=mock_user
        )

    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'

    self.c.request = {'json': '1'}
    self.c.response = self.mox.CreateMockAnything()
    self.c.response.out = self.mox.CreateMockAnything()
    self.c.response.out.write(
        handlers.JSON_PREFIX + '{"passphrase": "%s"}' % passphrase)

    mock_entity = self.mox.CreateMockAnything()
    mock_entity.passphrase = passphrase
    mock_entity.owner = 'mock_user_foo@example.com'

    self.mox.StubOutWithMock(models.LuksVolume, 'get_by_key_name')
    models.LuksVolume.get_by_key_name(volume_uuid).AndReturn(mock_entity)

    self.mox.StubOutWithMock(models.LuksAccessLog, 'Log')
    models.LuksAccessLog.Log(
        message='GET', entity=mock_entity, request=self.c.request)

    self.mox.StubOutWithMock(self.c, 'SendRetrievalEmail')
    self.c.SendRetrievalEmail(mock_entity, mock_user).AndReturn(None)

    self.mox.ReplayAll()
    self.c.RetrieveSecret(volume_uuid)
    self.mox.VerifyAll()

  def testNominal(self):
    volume_uuid = 'foovolumeuuid'
    passphrase = 'foopassphrase'
    mock_entity = self.mox.CreateMockAnything()
    mock_entity.passphrase = passphrase

    self.c.request = {'json': '1'}
    self.c.response = self.mox.CreateMockAnything()
    self.c.response.out = self.mox.CreateMockAnything()
    self.c.response.out.write(
        handlers.JSON_PREFIX + '{"passphrase": "%s"}' % passphrase)

    self.mox.StubOutWithMock(models, 'GetCurrentUser')
    models.GetCurrentUser().AndReturn('mock_user')

    self.mox.StubOutWithMock(self.c, 'VerifyXsrfToken')
    self.c.VerifyXsrfToken('RetrieveSecret')

    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.c.VerifyPermissions(permissions.RETRIEVE, user='mock_user')

    self.mox.StubOutWithMock(models.LuksVolume, 'get_by_key_name')
    models.LuksVolume.get_by_key_name(volume_uuid).AndReturn(
        mock_entity)

    self.mox.StubOutWithMock(models.LuksAccessLog, 'Log')
    models.LuksAccessLog.Log(
        message='GET', entity=mock_entity, request=self.c.request)

    self.mox.StubOutWithMock(self.c, 'SendRetrievalEmail')
    self.c.SendRetrievalEmail(mock_entity, 'mock_user').AndReturn(None)
    self.mox.ReplayAll()
    self.c.RetrieveSecret(volume_uuid)
    self.mox.VerifyAll()

  def testInvalidVolumeUUID(self):
    self.mox.StubOutWithMock(models, 'GetCurrentUser')
    models.GetCurrentUser().AndReturn('mock_user')

    self.mox.StubOutWithMock(self.c, 'VerifyXsrfToken')
    self.c.VerifyXsrfToken('RetrieveSecret')

    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.c.VerifyPermissions(
        permissions.RETRIEVE, user='mock_user'
        ).AndReturn('user')

    self.mox.StubOutWithMock(models.LuksVolume, 'get_by_key_name')
    volume_uuid = 'does-not-exist'
    models.LuksVolume.get_by_key_name(volume_uuid).AndReturn(None)

    self.mox.ReplayAll()
    self.assertRaises(
        models.AccessError, self.c.RetrieveSecret, volume_uuid)
    self.mox.VerifyAll()

  def testInvalidXsrfToken(self):
    self.c.request = {
        'json': '1',
        'xsrf-token': 'mock_xsrf_token',
        }
    self.mox.StubOutWithMock(handlers.util, 'XsrfTokenValidate')
    handlers.util.XsrfTokenValidate(
        self.c.request['xsrf-token'],
        handlers.base_settings.GET_PASSPHRASE_ACTION
        ).AndReturn(False)

    self.mox.ReplayAll()
    self.assertRaises(
        models.AccessDeniedError,
        self.c.RetrieveSecret, 'foovolumeuuid')
    self.mox.VerifyAll()

  def testMissingXsrfToken(self):
    self.c.request = {
        'json': '1',
        'xsrf-token': None,
        }

    self.assertRaises(
        models.AccessDeniedError,
        self.c.RetrieveSecret, 'foovolumeuuid')


class SendRetrievalEmailTest(mox.MoxTestBase):

  def setUp(self):
    super(SendRetrievalEmailTest, self).setUp()
    self.c = handlers.LuksAccessHandler()
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()

  def tearDown(self):
    super(SendRetrievalEmailTest, self).tearDown()
    self.testbed.deactivate()

  def testByPermListUser(self):
    mock_user = self.mox.CreateMockAnything(models.User)
    mock_user.user = self.mox.CreateMockAnything(users.User)
    mock_user.user.email = lambda: 'mock_user@example.com'
    mock_entity = self.mox.CreateMockAnything(models.LuksVolume)
    mock_entity.owner = 'mock_owner@example.com'
    self.mox.StubOutWithMock(util, 'SendEmail')
    self.mox.StubOutWithMock(settings, 'RETRIEVE_AUDIT_ADDRESSES')
    settings.RETRIEVE_AUDIT_ADDRESSES = ['mock_email2@example.com']
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')

    self.c.VerifyPermissions(permissions.SILENT_RETRIEVE, mock_user)
    util.SendEmail(
        [mock_user.user.email()] + settings.SILENT_AUDIT_ADDRESSES,
        mox.IsA(basestring), mox.IsA(basestring))
    self.mox.ReplayAll()
    self.c.SendRetrievalEmail(mock_entity, mock_user)
    self.mox.VerifyAll()

  def testByPermReadUser(self):
    mock_user = self.mox.CreateMockAnything(models.User)
    mock_user.user = self.mox.CreateMockAnything(users.User)
    mock_user.user.email = lambda: 'mock_user@example.com'
    mock_entity = self.mox.CreateMockAnything(models.LuksVolume)
    mock_entity.owner = 'mock_owner'
    self.mox.StubOutWithMock(util, 'SendEmail')
    self.mox.StubOutWithMock(settings, 'RETRIEVE_AUDIT_ADDRESSES')
    settings.RETRIEVE_AUDIT_ADDRESSES = ['mock_email2@example.com']
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')

    self.c.VerifyPermissions(
        permissions.SILENT_RETRIEVE, mock_user).AndRaise(
            models.AccessDeniedError('test'))
    owner_email = '%s@%s' % (
        mock_entity.owner, settings.DEFAULT_EMAIL_DOMAIN)
    user_email = mock_user.user.email()
    util.SendEmail(
        [owner_email, user_email] + settings.RETRIEVE_AUDIT_ADDRESSES,
        mox.IsA(basestring), mox.IsA(basestring))
    self.mox.ReplayAll()
    self.c.SendRetrievalEmail(mock_entity, mock_user)
    self.mox.VerifyAll()


class VerifyEscrowTest(mox.MoxTestBase):

  def setUp(self):
    super(VerifyEscrowTest, self).setUp()

    self.testbed = testbed.Testbed()
    self.testbed.activate()

    self.c = handlers.LuksAccessHandler()

  def tearDown(self):
    super(VerifyEscrowTest, self).tearDown()
    self.testbed.deactivate()

  def testNominal(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(models.LuksVolume, 'get_by_key_name')

    volume_uuid = 'foovolumeuuid'
    self.c.VerifyPermissions(permissions.ESCROW).AndReturn('user')
    models.LuksVolume.get_by_key_name(volume_uuid).AndReturn('anything')

    self.c.response = self.mox.CreateMockAnything()
    self.c.response.out = self.mox.CreateMockAnything()
    self.c.response.out.write('Escrow verified.')

    self.mox.ReplayAll()
    self.c.VerifyEscrow(volume_uuid)
    self.mox.VerifyAll()

  def testFail(self):
    self.mox.StubOutWithMock(self.c, 'VerifyPermissions')
    self.mox.StubOutWithMock(models.LuksVolume, 'get_by_key_name')

    volume_uuid = 'foovolumeuuid'
    self.c.VerifyPermissions(permissions.ESCROW).AndReturn('user')
    models.LuksVolume.get_by_key_name(volume_uuid).AndReturn(None)

    self.mox.StubOutWithMock(self.c, 'error')
    self.c.error(404).AndReturn(None)

    self.mox.ReplayAll()
    self.c.VerifyEscrow(volume_uuid)
    self.mox.VerifyAll()


def main(_):
  basetest.main()


if __name__ == '__main__':
  app.run()