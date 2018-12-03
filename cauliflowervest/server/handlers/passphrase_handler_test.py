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

import httplib
import urllib
import uuid



from absl.testing import absltest
from absl.testing import parameterized
import mock
import webtest

from google.appengine.api import users
from google.appengine.ext import deferred
from google.appengine.ext import testbed

from cauliflowervest import settings as base_settings
from cauliflowervest.server import main as gae_main
from cauliflowervest.server import permissions
from cauliflowervest.server import service_factory
from cauliflowervest.server import services
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import base
from cauliflowervest.server.models import volumes as models


class GetTest(test_util.BaseTest):

  def setUp(self):
    super(GetTest, self).setUp()
    self.testapp = webtest.TestApp(gae_main.app)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testVolumeUuidInvalid(self):
    resp = self.testapp.get(
        '/filevault/invalid-volume-uuid?json=1', status=httplib.BAD_REQUEST)
    self.assertIn('target_id is malformed', resp.body)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testVolumeUuidValid(self):
    vol_uuid = str(uuid.uuid4()).upper()
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        filevault_perms=[permissions.RETRIEVE_OWN],
    ).put()
    models.FileVaultVolume(
        owners=['stub7'],
        volume_uuid=vol_uuid,
        serial='stub',
        passphrase='stub_pass1',
        hdd_serial='stub',
        platform_uuid='stub',
    ).put()

    resp = self.testapp.get(
        '/filevault/%s?json=1' % vol_uuid, status=httplib.OK)
    self.assertIn('"passphrase": "stub_pass1"', resp.body)

    volumes = models.FileVaultVolume.all().fetch(None)
    self.assertEqual(1, len(volumes))
    self.assertTrue(volumes[0].force_rekeying)


class PutTest(test_util.BaseTest):

  def setUp(self):
    super(PutTest, self).setUp()
    self.testapp = webtest.TestApp(gae_main.app)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testOwnerInMetadata(self, *_):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4()).upper()
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        filevault_perms=[permissions.ESCROW],
    ).put()

    qs = {
        'hdd_serial': 'stub',
        'owner': 'stub9',
        'platform_uuid': 'stub',
        'serial': 'stub',
        'json': 1,
    }
    resp = self.testapp.put(
        '/filevault/%s?%s' % (vol_uuid, urllib.urlencode(qs)), params=secret)

    self.assertIn('successfully escrowed', resp.body)

    entity = models.FileVaultVolume.all().filter(
        'owners =', 'stub9@example.com').get()
    self.assertIsNotNone(entity)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testOwnerNotInMetadata(self, *_):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4()).upper()
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        filevault_perms=[permissions.ESCROW],
    ).put()

    qs = {
        'hdd_serial': '3uDR0LYQmN',
        'platform_uuid': 'stub',
        'serial': 'stub',
        'json': 1,
    }
    resp = self.testapp.put(
        '/filevault/%s?%s' % (vol_uuid, urllib.urlencode(qs)), params=secret)

    self.assertIn('successfully escrowed', resp.body)

    entity = models.FileVaultVolume.all().filter(
        'hdd_serial =', '3uDR0LYQmN').get()
    self.assertIsNotNone(entity)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testPutNonDefaultTag(self, *_):
    tag = 'keyslot3'
    secret = str(uuid.uuid4()).upper()
    volume_uuid = str(uuid.uuid4()).upper()
    params = {
        'hdd_serial': 'stub',
        'hostname': 'stub',
        'serial': 'stub',
        'platform_uuid': 'stub',
        'tag': tag,
    }
    resp = self.testapp.put(
        '/luks/%s?%s' % (volume_uuid, urllib.urlencode(params)), params=secret)

    self.assertEqual(httplib.OK, resp.status_int)
    self.assertEqual(tag, models.LuksVolume.all().fetch(1)[0].tag)


  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  @mock.patch.object(service_factory, 'GetInventoryService',
                     spec=services.InventoryService)
  def testUpdateMetadataDuringEscrow(self, get_intentory_service_mock, *_):
    inventory = get_intentory_service_mock.return_value
    inventory.GetMetadataUpdates.return_value = {
        'hostname': 'example2',
        'owners': ['zaspire', 'zerocool']
    }

    secret = str(uuid.uuid4()).upper()
    volume_uuid = str(uuid.uuid4()).upper()
    params = {
        'hdd_serial': 'stub',
        'hostname': 'stub',
        'serial': 'stub',
        'platform_uuid': 'stub',
    }

    self.testapp.put('/luks/%s?%s' % (volume_uuid, urllib.urlencode(params)),
                     params=secret)

    vols = models.LuksVolume.all().fetch(999)
    self.assertEqual(1, len(vols))
    self.assertEqual('example2', vols[0].hostname)
    self.assertEqual(['zaspire@example.com', 'zerocool@example.com'],
                     vols[0].owners)
    self.assertEqual(secret, vols[0].secret)


class RetrieveSecretTest(test_util.BaseTest):

  def setUp(self):
    super(RetrieveSecretTest, self).setUp()
    self.testapp = webtest.TestApp(gae_main.app)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testBarcode(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        luks_perms=[permissions.RETRIEVE_OWN],
    ).put()
    models.LuksVolume(
        owners=['stub7'],
        hdd_serial='stub',
        hostname='stub',
        passphrase=secret,
        platform_uuid='stub',
        volume_uuid=vol_uuid).put()
    with mock.patch.object(util, 'SendEmail') as _:
      resp = self.testapp.get('/luks/%s?json=1' % vol_uuid)

      o = util.FromSafeJson(resp.body)
      self.assertTrue(o['qr_img_url'])


  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testBarcodeTooLong(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4()) * 10
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        luks_perms=[permissions.RETRIEVE_OWN],
    ).put()
    models.LuksVolume(
        owners=['stub7'],
        hdd_serial='stub',
        hostname='stub',
        passphrase=secret,
        platform_uuid='stub',
        volume_uuid=vol_uuid).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = self.testapp.get('/luks/%s?json=1' % vol_uuid)

      o = util.FromSafeJson(resp.body)
      self.assertFalse(o['qr_img_url'])

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testNoPassphraseFound(self):
    vol_uuid = str(uuid.uuid4()).upper()
    resp = self.testapp.get('/filevault/%s?json=1' % vol_uuid,
                            status=httplib.NOT_FOUND)
    self.assertEqual('Passphrase not found: target_id %s' % vol_uuid, resp.body)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testCheckAuthzCreatorOk(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        filevault_perms=[permissions.RETRIEVE_CREATED_BY],
    ).put()
    models.FileVaultVolume(
        owners=['stub3'],
        created_by=users.User('stub7@example.com'),
        volume_uuid=vol_uuid,
        passphrase=secret,
        hdd_serial='stub',
        platform_uuid='stub',
        serial='stub',
    ).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = self.testapp.get('/filevault/%s?json=1' % vol_uuid,
                              status=httplib.OK)
    self.assertIn('"passphrase": "%s"' % secret, resp.body)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testCheckAuthzGlobalOk(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        filevault_perms=[permissions.RETRIEVE],
    ).put()
    volume_id = models.FileVaultVolume(
        owners=['stub2'],
        volume_uuid=vol_uuid,
        passphrase=secret,
        hdd_serial='stub',
        platform_uuid='stub',
        serial='stub',
    ).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = self.testapp.get(
          '/filevault/%s?json=1&id=%s' % (vol_uuid, volume_id),
          status=httplib.OK)
    self.assertIn('"passphrase": "%s"' % secret, resp.body)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testCheckAuthzOwnerFail(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        filevault_perms=[permissions.RETRIEVE_OWN],
    ).put()
    models.FileVaultVolume(
        owners=['stub2'],
        volume_uuid=vol_uuid,
        passphrase=secret,
        hdd_serial='stub',
        platform_uuid='stub',
        serial='stub',
    ).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = self.testapp.get('/filevault/%s?json=1' % vol_uuid,
                              status=httplib.FORBIDDEN)
      self.assertIn('Access denied.', resp.body)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testCheckAuthzOwnerOk(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        filevault_perms=[permissions.RETRIEVE_OWN],
    ).put()
    models.FileVaultVolume(
        owners=['stub7'],
        volume_uuid=vol_uuid,
        passphrase=secret,
        hdd_serial='stub',
        platform_uuid='stub',
        serial='stub',
    ).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = self.testapp.get('/filevault/%s?json=1' % vol_uuid,
                              status=httplib.OK)
    self.assertIn('"passphrase": "%s"' % secret, resp.body)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testLuksAsNonOwner(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        luks_perms=[permissions.RETRIEVE_OWN],
    ).put()
    models.LuksVolume(
        owners=['stub5'],
        hdd_serial='stub',
        hostname='stub',
        passphrase=secret,
        platform_uuid='stub',
        volume_uuid=vol_uuid).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = self.testapp.get('/luks/%s?json=1' % vol_uuid,
                              status=httplib.FORBIDDEN)
    self.assertIn('Access denied.', resp.body)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testLuksAsOwner(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        luks_perms=[permissions.RETRIEVE_OWN],
    ).put()
    models.LuksVolume(
        owners=['stub7'],
        hdd_serial='stub',
        hostname='stub',
        passphrase=secret,
        platform_uuid='stub',
        volume_uuid=vol_uuid).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = self.testapp.get('/luks/%s?json=1' % vol_uuid,
                              status=httplib.OK)
    self.assertIn('"passphrase": "%s"' % secret, resp.body)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testSilentRetrieve(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        luks_perms=[permissions.SILENT_RETRIEVE, permissions.RETRIEVE],
    ).put()
    models.LuksVolume(
        owners=['stub'],
        hdd_serial='stub',
        hostname='stub',
        passphrase=secret,
        platform_uuid='stub',
        volume_uuid=vol_uuid).put()

    with mock.patch.object(util, 'SendEmail') as mock_send_email:
      self.testapp.get('/luks/%s?json=1' % vol_uuid, status=httplib.OK)
      mock_send_email.assert_not_called()

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testProvisioningAsOwner(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        provisioning_perms=[permissions.RETRIEVE_OWN],
    ).put()
    models.ProvisioningVolume(
        owners=['stub7'],
        hdd_serial='stub',
        passphrase=secret,
        platform_uuid='stub',
        serial='stub',
        volume_uuid=vol_uuid,
    ).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = self.testapp.get('/provisioning/%s?json=1' % vol_uuid,
                              status=httplib.OK)
    self.assertIn('"passphrase": "%s"' % secret, resp.body)


class SendRetrievalEmailTest(test_util.BaseTest, parameterized.TestCase):

  def setUp(self):
    super(SendRetrievalEmailTest, self).setUp()
    self.testapp = webtest.TestApp(gae_main.app)

  def testSubjectConstantsExistForAllTypes(self):
    for escrow_type in permissions.TYPES:
      var_name = '%s_RETRIEVAL_EMAIL_SUBJECT' % escrow_type.upper()
      self.assertTrue(hasattr(settings, var_name))


  @mock.patch.dict(
      settings.__dict__, {
          'XSRF_PROTECTION_ENABLED': False,
          'SILENT_AUDIT_ADDRESSES': ['silent@example.com'],
      })
  def testByPermSilentWithAudit(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        email='stub7@example.com',
        provisioning_perms=[
            permissions.RETRIEVE, permissions.SILENT_RETRIEVE_WITH_AUDIT_EMAIL,
        ],
    ).put()
    models.ProvisioningVolume(
        owners=['stub6'],
        hdd_serial='stub',
        passphrase=secret,
        platform_uuid='stub',
        serial='stub',
        volume_uuid=vol_uuid,
    ).put()

    with mock.patch.object(util, 'SendEmail') as mock_send_email:
      self.testapp.get('/provisioning/%s?json=1' % vol_uuid)
      self.assertEqual(1, mock_send_email.call_count)
      recipients, _, _ = mock_send_email.call_args[0]
    self.assertEqual(['stub7@example.com', 'silent@example.com'], recipients)

  @parameterized.parameters(
      ('stub2', u'stub2@example.com'),
      ('stub2@example.com', u'stub2@example.com'))
  @mock.patch.dict(
      settings.__dict__, {
          'XSRF_PROTECTION_ENABLED': False,
          'RETRIEVE_AUDIT_ADDRESSES': ['retr@example.com'],
          'DEFAULT_EMAIL_DOMAIN': 'example.com',
      })
  def testByPermRead(self, owner, expected_email):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        email='stub7@example.com',
        provisioning_perms=[permissions.RETRIEVE],
        ).put()
    models.ProvisioningVolume(
        owners=[owner],
        hdd_serial='stub',
        passphrase=secret,
        platform_uuid='stub',
        serial='stub',
        volume_uuid=vol_uuid,
    ).put()

    with mock.patch.object(util, 'SendEmail') as mock_send_email:
      self.testapp.get('/provisioning/%s?json=1' % vol_uuid)
      self.assertEqual(1, mock_send_email.call_count)
      recipients, _, _ = mock_send_email.call_args[0]
    self.assertItemsEqual(
        ['stub7@example.com', expected_email, 'retr@example.com'],
        recipients)


if __name__ == '__main__':
  absltest.main()
