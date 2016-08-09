#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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
"""search module tests."""



import datetime
import httplib
import json
import os
import uuid


import mock

from google.appengine.api import users

from google.apputils import app
from google.apputils import basetest

from cauliflowervest.server import handlers
from cauliflowervest.server import main as gae_main
from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server.handlers import search
from tests.cauliflowervest.server.handlers import test_util


class SearchModuleTest(basetest.TestCase):
  """Test the search module."""

  def setUp(self):
    super(SearchModuleTest, self).setUp()

    test_util.SetUpTestbedTestCase(self)

    models.BitLockerVolume(
        owner='stub', dn='CN;',
        created_by=search.users.User('foouser@example.com'),
        recovery_key=str(uuid.uuid4()), parent_guid=str(uuid.uuid4()).upper(),
        hostname=models.BitLockerVolume.NormalizeHostname('workstation'),
        volume_uuid=str(uuid.uuid4()).upper()
        ).put()
    models.BitLockerVolume(
        owner='stub7', created_by=search.users.User('other@example.com'),
        dn='CN;', recovery_key=str(uuid.uuid4()),
        parent_guid=str(uuid.uuid4()).upper(),
        hostname=models.BitLockerVolume.NormalizeHostname('foohost'),
        volume_uuid=str(uuid.uuid4()).upper()
        ).put()

  def tearDown(self):
    super(SearchModuleTest, self).tearDown()
    test_util.TearDownTestbedTestCase(self)

  def testMainPageRedirect(self):
    resp = gae_main.app.get_response(
        '/search', {'REQUEST_METHOD': 'GET'})

    self.assertEqual(httplib.FOUND, resp.status_int)
    self.assertEqual('http://localhost/ui/', resp.location)

  def testSearchRedirect(self):
    resp = gae_main.app.get_response(
        '/search?search_type=luks&field1=owner&value1=zaspire',
        {'REQUEST_METHOD': 'GET'})

    self.assertEqual(httplib.FOUND, resp.status_int)
    self.assertEqual(
        'http://localhost/ui/#/search/luks/owner/zaspire/0', resp.location)

  @mock.patch.dict(
      handlers.settings.__dict__, {'XSRF_PROTECTION_ENABLED': False})
  def testApiNoRedirect(self):
    resp = gae_main.app.get_response(
        '/search?search_type=luks&field1=owner&value1=zaspire&json=1',
        {'REQUEST_METHOD': 'GET'})

    self.assertEqual(httplib.OK, resp.status_int)

  def testVolumesForQueryCreatedBy(self):
    created_by = 'foouser'
    email = '%s@%s' % (created_by, os.environ['AUTH_DOMAIN'])

    query = 'created_by:%s' % created_by
    volumes = search.VolumesForQuery(query, 'bitlocker')

    self.assertEqual(1, len(volumes))
    self.assertEqual(email, volumes[0].created_by.email())

  def testVolumesForQueryHostname(self):
    hostname = 'foohost'
    query = 'hostname:%s' % hostname

    volumes = search.VolumesForQuery(query, 'bitlocker')

    self.assertEqual(1, len(volumes))
    self.assertEqual(models.BitLockerVolume.NormalizeHostname(hostname),
                     volumes[0].hostname)

  def testVolumesForQueryPrefix(self):
    query = 'owner:stub'
    volumes = search.VolumesForQuery(query, 'bitlocker', prefix_search=True)

    self.assertEqual(2, len(volumes))

  def testVolumesForQueryOwner(self):
    # Searching by owner with domain (e.g., example.com) in query should
    # return the volume if the owner in datastore doesn't have domain. I.e.,
    # searching for "lololol@example.com" should still find volumes with
    # owner="lololol".
    models.BitLockerVolume(
        owner='lololol',
        created_by=search.users.User('other@example.com'),
        dn='CN;', recovery_key=str(uuid.uuid4()),
        parent_guid=str(uuid.uuid4()).upper(),
        hostname=models.BitLockerVolume.NormalizeHostname('lololol'),
        volume_uuid=str(uuid.uuid4()).upper()
        ).put()
    volumes = search.VolumesForQuery('owner:lololol@example.com', 'bitlocker')
    self.assertEqual(1, len(volumes))
    self.assertEqual(
        models.BitLockerVolume.NormalizeHostname('lololol'),
        volumes[0].hostname)

    # Searching by owner without domain (e.g., example.com) in query should
    # still return the volume if the owner in datastore does have domain. I.e.,
    # searching for "stub1337" should still find volumes with
    # owner="stub1337@example.com".
    models.BitLockerVolume(
        owner='stub1337@example.com',
        created_by=search.users.User('other@example.com'),
        dn='CN;', recovery_key=str(uuid.uuid4()),
        parent_guid=str(uuid.uuid4()).upper(),
        hostname=models.BitLockerVolume.NormalizeHostname('stub1337'),
        volume_uuid=str(uuid.uuid4()).upper()
        ).put()
    volumes = search.VolumesForQuery('owner:stub1337', 'bitlocker')
    self.assertEqual(1, len(volumes))
    self.assertEqual(
        models.BitLockerVolume.NormalizeHostname('stub1337'),
        volumes[0].hostname)

  @mock.patch.dict(
      search.__dict__, {'MAX_VOLUMES_PER_QUERY': 20})
  def testProvisioningVolumesForQueryCreatedBy(self):
    models.ProvisioningVolume.created.auto_now = False

    today = datetime.datetime.today()

    for i in range(2 * search.MAX_VOLUMES_PER_QUERY):
      models.ProvisioningVolume(
          owner='stub', serial='stub', volume_uuid=str(uuid.uuid4()),
          created_by=users.User('stub@example.com'), hdd_serial='stub',
          passphrase=str(uuid.uuid4()), platform_uuid='stub',
          created=today - datetime.timedelta(days=i),
          ).put()
    volumes = search.VolumesForQuery('created_by:stub@example.com',
                                     permissions.TYPE_PROVISIONING, False)

    self.assertEqual(search.MAX_VOLUMES_PER_QUERY, len(volumes))
    for i in range(search.MAX_VOLUMES_PER_QUERY):
      self.assertEqual(users.User('stub@example.com'), volumes[i].created_by)
      self.assertEqual(today - datetime.timedelta(days=i),
                       volumes[i].created)

    models.ProvisioningVolume.created.auto_now = True



def main(_):
  basetest.main()


if __name__ == '__main__':
  app.run()
