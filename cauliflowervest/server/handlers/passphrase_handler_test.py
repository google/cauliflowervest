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



import mock

from google.appengine.api import users
from google.appengine.ext import deferred
from google.appengine.ext import testbed


from absl.testing import absltest

from cauliflowervest import settings as base_settings
from cauliflowervest.server import main as gae_main
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import base
from cauliflowervest.server.models import volumes as models


class GetTest(test_util.BaseTest):

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testVolumeUuidInvalid(self):
    resp = gae_main.app.get_response('/filevault/invalid-volume-uuid?json=1')
    self.assertEqual(httplib.BAD_REQUEST, resp.status_int)
    self.assertIn('target_id is malformed', resp.body)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testVolumeUuidValid(self):
    vol_uuid = str(uuid.uuid4()).upper()
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        filevault_perms=[permissions.RETRIEVE_OWN],
    ).put()
    models.FileVaultVolume(
        owner='stub7', volume_uuid=vol_uuid, serial='stub',
        passphrase='stub_pass1', hdd_serial='stub', platform_uuid='stub',
    ).put()

    resp = gae_main.app.get_response('/filevault/%s?json=1' % vol_uuid)
    self.assertEqual(httplib.OK, resp.status_int)
    self.assertIn('"passphrase": "stub_pass1"', resp.body)

    volumes = models.FileVaultVolume.all().fetch(None)
    self.assertEqual(1, len(volumes))
    self.assertTrue(volumes[0].force_rekeying)


class PutTest(test_util.BaseTest):

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testOwnerInMetadata(self):
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
    resp = gae_main.app.get_response(
        '/filevault/%s?%s' % (vol_uuid, urllib.urlencode(qs)),
        {'REQUEST_METHOD': 'PUT'},
        POST=secret)

    self.assertIn('successfully escrowed', resp.body)

    entity = models.FileVaultVolume.all().filter(
        'owner =', 'stub9@example.com').get()
    self.assertIsNotNone(entity)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testOwnerNotInMetadata(self):
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
    resp = gae_main.app.get_response(
        '/filevault/%s?%s' % (vol_uuid, urllib.urlencode(qs)),
        {'REQUEST_METHOD': 'PUT'},
        POST=secret)

    self.assertIn('successfully escrowed', resp.body)

    entity = models.FileVaultVolume.all().filter(
        'hdd_serial =', '3uDR0LYQmN').get()
    self.assertIsNotNone(entity)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testPutNonDefaultTag(self):
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
    resp = gae_main.app.get_response(
        '/luks/%s?%s' % (volume_uuid, urllib.urlencode(params)),
        {'REQUEST_METHOD': 'PUT'},
        POST=secret)

    self.assertEqual(httplib.OK, resp.status_int)
    self.assertEqual(tag, models.LuksVolume.all().fetch(1)[0].tag)



class RetrieveSecretTest(test_util.BaseTest):

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testBarcode(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        luks_perms=[permissions.RETRIEVE_OWN],
    ).put()
    models.LuksVolume(
        owner='stub7', hdd_serial='stub', hostname='stub', passphrase=secret,
        platform_uuid='stub', volume_uuid=vol_uuid
    ).put()
    with mock.patch.object(util, 'SendEmail') as _:
      resp = gae_main.app.get_response('/luks/%s?json=1' % vol_uuid)

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
        owner='stub7', hdd_serial='stub', hostname='stub', passphrase=secret,
        platform_uuid='stub', volume_uuid=vol_uuid
    ).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = gae_main.app.get_response('/luks/%s?json=1' % vol_uuid)

      o = util.FromSafeJson(resp.body)
      self.assertFalse(o['qr_img_url'])

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testCheckAuthzCreatorOk(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        filevault_perms=[permissions.RETRIEVE_CREATED_BY],
    ).put()
    models.FileVaultVolume(
        owner='stub3',
        created_by=users.User('stub7@example.com'),
        volume_uuid=vol_uuid, passphrase=secret,
        hdd_serial='stub', platform_uuid='stub', serial='stub',
    ).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = gae_main.app.get_response('/filevault/%s?json=1' % vol_uuid)
    self.assertEqual(httplib.OK, resp.status_int)
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
        owner='stub2', volume_uuid=vol_uuid, passphrase=secret,
        hdd_serial='stub', platform_uuid='stub', serial='stub',
    ).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = gae_main.app.get_response(
          '/filevault/%s?json=1&id=%s' % (vol_uuid, volume_id))
      self.assertEqual(httplib.OK, resp.status_int)
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
        owner='stub2', volume_uuid=vol_uuid, passphrase=secret,
        hdd_serial='stub', platform_uuid='stub', serial='stub',
    ).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = gae_main.app.get_response('/filevault/%s?json=1' % vol_uuid)
      self.assertEqual(httplib.FORBIDDEN, resp.status_int)
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
        owner='stub7', volume_uuid=vol_uuid, passphrase=secret,
        hdd_serial='stub', platform_uuid='stub', serial='stub',
    ).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = gae_main.app.get_response('/filevault/%s?json=1' % vol_uuid)
    self.assertEqual(httplib.OK, resp.status_int)
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
        owner='stub5', hdd_serial='stub', hostname='stub', passphrase=secret,
        platform_uuid='stub', volume_uuid=vol_uuid
    ).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = gae_main.app.get_response('/luks/%s?json=1' % vol_uuid)
    self.assertEqual(httplib.FORBIDDEN, resp.status_int)
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
        owner='stub7', hdd_serial='stub', hostname='stub', passphrase=secret,
        platform_uuid='stub', volume_uuid=vol_uuid
    ).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = gae_main.app.get_response('/luks/%s?json=1' % vol_uuid)
    self.assertEqual(httplib.OK, resp.status_int)
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
        owner='stub', hdd_serial='stub', hostname='stub', passphrase=secret,
        platform_uuid='stub', volume_uuid=vol_uuid
    ).put()

    with mock.patch.object(util, 'SendEmail') as mock_send_email:
      resp = gae_main.app.get_response('/luks/%s?json=1' % vol_uuid)
      mock_send_email.assert_not_called()
    self.assertEqual(httplib.OK, resp.status_int)

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testProvisioningAsOwner(self):
    vol_uuid = str(uuid.uuid4()).upper()
    secret = str(uuid.uuid4())
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        provisioning_perms=[permissions.RETRIEVE_OWN],
    ).put()
    models.ProvisioningVolume(
        owner='stub7', hdd_serial='stub', passphrase=secret,
        platform_uuid='stub', serial='stub',
        volume_uuid=vol_uuid,
    ).put()

    with mock.patch.object(util, 'SendEmail') as _:
      resp = gae_main.app.get_response(
          '/provisioning/%s?json=1' % vol_uuid)
    self.assertEqual(httplib.OK, resp.status_int)
    self.assertIn('"passphrase": "%s"' % secret, resp.body)




if __name__ == '__main__':
  absltest.main()
