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

"""search module tests."""

import datetime
import httplib
import os
import uuid



from absl.testing import absltest
import mock
import webtest

from google.appengine.api import users

from cauliflowervest.server import main as gae_main
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import search
from cauliflowervest.server.handlers import test_util
from cauliflowervest.server.models import base
from cauliflowervest.server.models import firmware
from cauliflowervest.server.models import volumes as models


class SearchModuleTest(test_util.BaseTest):
  """Test the search module."""

  def setUp(self):
    super(SearchModuleTest, self).setUp()

    models.BitLockerVolume(
        owners=['stub', 'unrelated'],
        dn='CN;',
        created_by=search.users.User('foouser@example.com'),
        recovery_key=str(uuid.uuid4()),
        parent_guid=str(uuid.uuid4()).upper(),
        hostname=models.BitLockerVolume.NormalizeHostname('workstation'),
        volume_uuid=str(uuid.uuid4()).upper(),
        recovery_guid='guid',
    ).put()
    models.BitLockerVolume(
        owners=['stub7'],
        created_by=search.users.User('other@example.com'),
        dn='CN;',
        recovery_key=str(uuid.uuid4()),
        parent_guid=str(uuid.uuid4()).upper(),
        hostname=models.BitLockerVolume.NormalizeHostname('foohost'),
        volume_uuid=str(uuid.uuid4()).upper(),
        recovery_guid='guid',
    ).put()

    self.testapp = webtest.TestApp(gae_main.app)

  def testMainPageRedirect(self):
    resp = self.testapp.get('/search')

    self.assertEqual(httplib.MOVED_PERMANENTLY, resp.status_int)
    self.assertEqual('http://localhost/ui/', resp.location)

  def testSearchRedirect(self):
    resp = self.testapp.get(
        '/search?search_type=luks&field1=owner&value1=zaspire',
        status=httplib.FOUND)

    self.assertEqual(
        'http://localhost/ui/#/search/luks/owner/zaspire/0', resp.location)

  def testFilterResult(self):
    base.User(
        key_name='stub7@example.com', user=users.get_current_user(),
        bitlocker_perms=[permissions.RETRIEVE_OWN],
    ).put()

    resp = util.FromSafeJson(self.testapp.get(
        '/search?search_type=bitlocker&field1=owner&value1=stub&json=1').body)

    self.assertTrue(resp['results_access_warning'])
    self.assertEqual(0, len(resp['passphrases']))

  @mock.patch.dict(settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testApiNoRedirect(self):
    self.testapp.get(
        '/search?search_type=luks&field1=owner&value1=zaspire&json=1',
        status=httplib.OK)

  def testPassphrasesFoQueryCreatedBy(self):
    created_by = 'foouser'
    email = '%s@%s' % (created_by, os.environ['AUTH_DOMAIN'])

    volumes = search._PassphrasesForQuery(
        models.BitLockerVolume, 'created_by', created_by)

    self.assertEqual(1, len(volumes))
    self.assertEqual(email, volumes[0].created_by.email())

  def testPassphrasesForQueryHostname(self):
    hostname = 'foohost'

    volumes = search._PassphrasesForQuery(
        models.BitLockerVolume, 'hostname', hostname)

    self.assertEqual(1, len(volumes))
    self.assertEqual(models.BitLockerVolume.NormalizeHostname(hostname),
                     volumes[0].hostname)

  def testPassphrasesForQueryPrefix(self):
    volumes = search._PassphrasesForQuery(
        models.BitLockerVolume, 'owner', 'stub', prefix_search=True)

    self.assertEqual(2, len(volumes))

  def testPassphrasesForQueryOwner(self):
    # Searching by owner with domain (e.g., example.com) in query should
    # return the volume if the owner in datastore doesn't have domain. I.e.,
    # searching for "lololol@example.com" should still find volumes with
    # owner="lololol".
    models.BitLockerVolume(
        owners=['lololol'],
        created_by=search.users.User('other@example.com'),
        dn='CN;',
        recovery_key=str(uuid.uuid4()),
        parent_guid=str(uuid.uuid4()).upper(),
        hostname=models.BitLockerVolume.NormalizeHostname('lololol'),
        volume_uuid=str(uuid.uuid4()).upper(),
        recovery_guid='guid1',
    ).put()
    volumes = search._PassphrasesForQuery(
        models.BitLockerVolume, 'owner', 'lololol@example.com')
    self.assertEqual(1, len(volumes))
    self.assertEqual(
        models.BitLockerVolume.NormalizeHostname('lololol'),
        volumes[0].hostname)

    # Searching by owner without domain (e.g., example.com) in query should
    # still return the volume if the owner in datastore does have domain. I.e.,
    # searching for "stub1337" should still find volumes with
    # owner="stub1337@example.com".
    models.BitLockerVolume(
        owners=['stub1337@example.com'],
        created_by=search.users.User('other@example.com'),
        dn='CN;',
        recovery_key=str(uuid.uuid4()),
        parent_guid=str(uuid.uuid4()).upper(),
        recovery_guid='guid123',
        hostname=models.BitLockerVolume.NormalizeHostname('stub1337'),
        volume_uuid=str(uuid.uuid4()).upper()).put()
    volumes = search._PassphrasesForQuery(
        models.BitLockerVolume, 'owner', 'stub1337')
    self.assertEqual(1, len(volumes))
    self.assertEqual(
        models.BitLockerVolume.NormalizeHostname('stub1337'),
        volumes[0].hostname)

  @mock.patch.dict(
      search.__dict__, {'MAX_PASSPHRASES_PER_QUERY': 20})
  def testProvisioningQueryCreatedBySortingOrder(self):
    models.ProvisioningVolume.created.auto_now = False

    today = datetime.datetime.today()

    for i in range(2 * search.MAX_PASSPHRASES_PER_QUERY):
      models.ProvisioningVolume(
          owners=['stub7'],
          serial='stub',
          volume_uuid=str(uuid.uuid4()),
          created_by=users.User('stub7@example.com'),
          hdd_serial='stub',
          passphrase=str(uuid.uuid4()),
          platform_uuid='stub',
          created=today - datetime.timedelta(days=i),
      ).put()
    resp = util.FromSafeJson(self.testapp.get(
        '/search?search_type=provisioning&'
        'field1=created_by&value1=stub7@example.com&json=1').body)
    self.assertTrue(resp['too_many_results'])
    volumes = resp['passphrases']

    self.assertEqual(search.MAX_PASSPHRASES_PER_QUERY, len(volumes))
    for i in range(search.MAX_PASSPHRASES_PER_QUERY):
      self.assertEqual('stub7', volumes[i]['created_by'])
      self.assertEqual(str(today - datetime.timedelta(days=i)),
                       volumes[i]['created'])

    models.ProvisioningVolume.created.auto_now = True

  def testAppleFirmwareSearch(self):
    firmware.AppleFirmwarePassword(
        owners=['stub7'],
        serial='stub',
        created_by=users.User('stub@example.com'),
        password=str(uuid.uuid4()),
        platform_uuid='stub',
        hostname='host1').put()

    resp = self.testapp.get(
        '/search?search_type=apple_firmware&field1=owner&value1=stub7&json=1')
    self.assertEqual(1, len(util.FromSafeJson(resp.body)['passphrases']))

  def testLinuxFirmwareSearch(self):
    firmware.LinuxFirmwarePassword(
        owners=['stub7'],
        serial='stub',
        created_by=users.User('stub@example.com'),
        password=str(uuid.uuid4()),
        machine_uuid='stub',
        hostname='host1',
        manufacturer='Vendor',
    ).put()

    resp = self.testapp.get(
        '/search?search_type=linux_firmware&field1=owner&value1=stub7&json=1')
    self.assertEqual(1, len(util.FromSafeJson(resp.body)['passphrases']))

  def testWindowsFirmwareSearch(self):
    firmware.WindowsFirmwarePassword(
        owners=['stub7'],
        serial='stub',
        created_by=users.User('stub@example.com'),
        password=str(uuid.uuid4()),
        smbios_guid='stub',
        hostname='host1').put()

    resp = self.testapp.get(
        '/search?search_type=windows_firmware&field1=owner&value1=stub7&json=1')
    self.assertEqual(1, len(util.FromSafeJson(resp.body)['passphrases']))



if __name__ == '__main__':
  absltest.main()
