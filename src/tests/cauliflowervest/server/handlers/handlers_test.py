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

"""handlers module tests."""

import urllib
import uuid

import mock

from django.conf import settings
settings.configure()

from google.appengine.api import users
from google.appengine.ext import testbed

from google.apputils import app
from google.apputils import basetest

from cauliflowervest.server import crypto
from cauliflowervest.server import handlers
from cauliflowervest.server import main as gae_main
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util


class _BaseCase(basetest.TestCase):

  def setUp(self):
    super(_BaseCase, self).setUp()
    self.testbed = testbed.Testbed()

    # The oauth_aware decorator will 302 to login unless there is either
    # a current user _or_ a valid oauth header; this is easier to stub.
    self.testbed.setup_env(
        user_email='stub@gmail.com', user_id='1234', overwrite=True)

    self.testbed.activate()
    self.testbed.init_all_stubs()

    # Lazily mock out key-fetching RPC dependency.
    crypto.Decrypt = lambda x: x
    crypto.Encrypt = lambda x: x

  def tearDown(self):
    super(_BaseCase, self).tearDown()
    self.testbed.deactivate()


class GetTest(_BaseCase):

  def testVolumeUuidInvalid(self):
    resp = gae_main.app.get_response('/filevault/invalid-volume-uuid')
    self.assertEqual(400, resp.status_int)
    self.assertIn('volume_uuid is malformed', resp.body)

  def testVolumeUuidValid(self):
    vol_uuid = str(uuid.uuid4()).upper()
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        filevault_perms=[permissions.RETRIEVE_OWN],
        ).put()
    models.FileVaultVolume(
        key_name=vol_uuid, owner='stub',
        volume_uuid=vol_uuid, passphrase='stub_pass1',
        hdd_serial='stub', platform_uuid='stub', serial='stub',
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      resp = gae_main.app.get_response('/filevault/' + vol_uuid)
    self.assertEqual(200, resp.status_int)
    self.assertIn('"passphrase": "stub_pass1"', resp.body)

  def testOnlyVerify(self):
    vol_uuid = str(uuid.uuid4()).upper()
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        filevault_perms=[permissions.RETRIEVE_OWN],
        ).put()
    models.FileVaultVolume(
        key_name=vol_uuid, owner='stub',
        volume_uuid=vol_uuid, passphrase='stub_pass2',
        hdd_serial='stub', platform_uuid='stub', serial='stub',
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      resp = gae_main.app.get_response(
          '/filevault/%s?only_verify_escrow=1' % vol_uuid)
    self.assertEqual(200, resp.status_int)
    self.assertIn('Escrow verified', resp.body)


class PutTest(_BaseCase):

  def testOwnerInMetadata(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4()).upper()
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        filevault_perms=[permissions.ESCROW],
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False

      qs = {
          'hdd_serial': 'stub',
          'owner': 'stub9',
          'platform_uuid': 'stub',
          'serial': 'stub',
          }
      resp = gae_main.app.get_response(
          '/filevault/%s?%s' % (vol_uuid, urllib.urlencode(qs)),
          {'REQUEST_METHOD': 'PUT'},
          POST=secret)

      self.assertIn('successfully escrowed', resp.body)

    entity = models.FileVaultVolume.all().filter('owner =', 'stub9').get()
    self.assertIsNotNone(entity)

  def testOwnerNotInMetadata(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4()).upper()
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        filevault_perms=[permissions.ESCROW],
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False

      qs = {
          'hdd_serial': '3uDR0LYQmN',
          'platform_uuid': 'stub',
          'serial': 'stub',
          }
      resp = gae_main.app.get_response(
          '/filevault/%s?%s' % (vol_uuid, urllib.urlencode(qs)),
          {'REQUEST_METHOD': 'PUT'},
          POST=secret)

      self.assertIn('successfully escrowed', resp.body)

    entity = models.FileVaultVolume.all().filter(
        'hdd_serial =', '3uDR0LYQmN').get()
    self.assertIsNotNone(entity)



class RetrieveSecretTest(_BaseCase):

  def testBarcode(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        luks_perms=[permissions.RETRIEVE_OWN],
        ).put()
    models.LuksVolume(
        key_name=vol_uuid, owner='stub',
        hdd_serial='stub', hostname='stub', passphrase=secret,
        platform_uuid='stub',
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      with mock.patch.object(util, 'SendEmail') as _:
        resp = gae_main.app.get_response('/luks/%s?json=0' % vol_uuid)
        self.assertIn('<img class="qr_code" ', resp.body)

  def testBarcodeTooLong(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4()) * 10
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        luks_perms=[permissions.RETRIEVE_OWN],
        ).put()
    models.LuksVolume(
        key_name=vol_uuid, owner='stub',
        hdd_serial='stub', hostname='stub', passphrase=secret,
        platform_uuid='stub',
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      with mock.patch.object(util, 'SendEmail') as _:
        resp = gae_main.app.get_response('/luks/%s?json=0' % vol_uuid)
        self.assertNotIn('<img class="qr_code" ', resp.body)

  def testCheckAuthzCreatorOk(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        filevault_perms=[permissions.RETRIEVE_CREATED_BY],
        ).put()
    models.FileVaultVolume(
        key_name=vol_uuid, owner='stub3',
        creator='stub@gmail.com',
        volume_uuid=vol_uuid, passphrase=secret,
        hdd_serial='stub', platform_uuid='stub', serial='stub',
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      with mock.patch.object(util, 'SendEmail') as _:
        resp = gae_main.app.get_response('/filevault/' + vol_uuid)
        self.assertEqual(200, resp.status_int)
        self.assertIn('"passphrase": "%s"' % secret, resp.body)

  def testCheckAuthzGlobalOk(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        filevault_perms=[permissions.RETRIEVE],
        ).put()
    models.FileVaultVolume(
        key_name=vol_uuid, owner='stub2',
        volume_uuid=vol_uuid, passphrase=secret,
        hdd_serial='stub', platform_uuid='stub', serial='stub',
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      with mock.patch.object(util, 'SendEmail') as _:
        resp = gae_main.app.get_response('/filevault/' + vol_uuid)
        self.assertEqual(200, resp.status_int)
        self.assertIn('"passphrase": "%s"' % secret, resp.body)

  def testCheckAuthzOwnerFail(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        filevault_perms=[permissions.RETRIEVE_OWN],
        ).put()
    models.FileVaultVolume(
        key_name=vol_uuid, owner='stub2',
        volume_uuid=vol_uuid, passphrase=secret,
        hdd_serial='stub', platform_uuid='stub', serial='stub',
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      with mock.patch.object(util, 'SendEmail') as _:
        resp = gae_main.app.get_response('/filevault/' + vol_uuid)
        self.assertEqual(400, resp.status_int)
        self.assertIn('Not authorized', resp.body)

  def testCheckAuthzOwnerOk(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        filevault_perms=[permissions.RETRIEVE_OWN],
        ).put()
    models.FileVaultVolume(
        key_name=vol_uuid, owner='stub',
        volume_uuid=vol_uuid, passphrase=secret,
        hdd_serial='stub', platform_uuid='stub', serial='stub',
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      with mock.patch.object(util, 'SendEmail') as _:
        resp = gae_main.app.get_response('/filevault/' + vol_uuid)
        self.assertEqual(200, resp.status_int)
        self.assertIn('"passphrase": "%s"' % secret, resp.body)

  def testLuksAsNonOwner(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        luks_perms=[permissions.RETRIEVE_OWN],
        ).put()
    models.LuksVolume(
        key_name=vol_uuid, owner='stub5',
        hdd_serial='stub', hostname='stub', passphrase=secret,
        platform_uuid='stub',
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      with mock.patch.object(util, 'SendEmail') as _:
        resp = gae_main.app.get_response('/luks/' + vol_uuid)
        self.assertEqual(400, resp.status_int)
        self.assertIn('Not authorized', resp.body)

  def testLuksAsOwner(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        luks_perms=[permissions.RETRIEVE_OWN],
        ).put()
    models.LuksVolume(
        key_name=vol_uuid, owner='stub',
        hdd_serial='stub', hostname='stub', passphrase=secret,
        platform_uuid='stub',
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      with mock.patch.object(util, 'SendEmail') as _:
        resp = gae_main.app.get_response('/luks/' + vol_uuid)
        self.assertEqual(200, resp.status_int)
        self.assertIn('"passphrase": "%s"' % secret, resp.body)

  def testProvisioningAsOwner(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        provisioning_perms=[permissions.RETRIEVE_OWN],
        ).put()
    models.ProvisioningVolume(
        key_name=vol_uuid, owner='stub',
        hdd_serial='stub', passphrase=secret,
        platform_uuid='stub', serial='stub', volume_uuid='stub',
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      with mock.patch.object(util, 'SendEmail') as _:
        resp = gae_main.app.get_response('/provisioning/' + vol_uuid)
        self.assertEqual(200, resp.status_int)
        self.assertIn('"passphrase": "%s"' % secret, resp.body)




class VerifyEscrowTest(_BaseCase):

  def testFail(self):
    vol_uuid = str(uuid.uuid4()).upper()
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        email='stub@gmail.com', provisioning_perms=[permissions.RETRIEVE],
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      resp = gae_main.app.get_response(
          '/bitlocker/%s?only_verify_escrow=1' % vol_uuid)
      self.assertEquals(404, resp.status_int)

  def testSucceed(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    models.User(
        key_name='stub@gmail.com', user=users.get_current_user(),
        email='stub@gmail.com',
        provisioning_perms=[permissions.RETRIEVE],
        ).put()
    models.BitLockerVolume(
        key_name=vol_uuid, owner='stub',
        dn='stub', hostname='stub', parent_guid='stub', recovery_key=secret,
        ).put()

    with mock.patch.object(handlers, 'settings') as mock_settings:
      mock_settings.XSRF_PROTECTION_ENABLED = False
      resp = gae_main.app.get_response(
          '/bitlocker/%s?only_verify_escrow=1' % vol_uuid)
      self.assertEqual(200, resp.status_int)
      self.assertIn('Escrow verified', resp.body)


def main(_):
  basetest.main()


if __name__ == '__main__':
  app.run()
