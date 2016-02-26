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
"""Tests for BitLocker AD Sync module."""



import unittest

import mox
import stubout

# NOTE(user): mock ldap import as it fails to build on OS X 10.9.
import sys
class MockLdapModule(object):
  class controls(object):
      pass
  def __getattr__(self, k):
    return k.lower()
if 'ldap' not in sys.modules:
  sys.modules['ldap'] = MockLdapModule()

from cauliflowervest.client.win import bitlocker_ad_sync


class BitLockerAdSyncTest(mox.MoxTestBase):
  """Test the bitlocker_ad_sync.BitLockerAdSync class."""

  def setUp(self):
    super(BitLockerAdSyncTest, self).setUp()
    self.mox = mox.Mox()
    self.mock_client = self.mox.CreateMockAnything()
    self.c = bitlocker_ad_sync.BitLockerAdSync(
        client=self.mock_client)
    bitlocker_ad_sync.FLAGS.redact_recovery_passwords = False

  def tearDown(self):
    self.mox.UnsetStubs()

  def testProcessHost(self):
    parent_dn = 'CN=HOSTNAME,OU=Workstations,DC=ad,DC=example,DC=com'
    dn = ('CN=2011-01-05T17:30:35-08:00{19874ADC-1B13-3E60-BA01-BBFAFE18C794},'
          + parent_dn)
    hostname = 'HOSTNAME'
    recovery_guid_bytes = 'd0\'\xa3\xb8[sJ\x92\x81M\xa7&\x1a\x96g'
    recovery_guid = 'A3273064-5BB8-4A73-9281-4DA7261A9667'
    parent_guid_bytes = '`\xb7\x1b\xbd\x92i\xd8L\x82\xe8B\x0bmI\x13/'
    parent_guid = 'BD1BB760-6992-4CD8-82E8-420B6D49132F'
    recovery_password = 'foopassword'
    when_created = '20120315181002.0Z'
    ldap_msfve = {
        'distinguishedName': [dn],
        'msFVE-RecoveryGuid': [recovery_guid_bytes],
        'msFVE-RecoveryPassword': [recovery_password],
        'whenCreated': [when_created],
    }
    ldap_host = {
        'objectGUID': [parent_guid_bytes],
    }
    metadata = {
        'dn': dn,
        'hostname': hostname,
        'parent_guid': parent_guid,
        'when_created': when_created
    }

    self.mox.StubOutWithMock(self.c, '_QueryLdap')
    ldap_scope = bitlocker_ad_sync.ldap.SCOPE_BASE
    self.c._QueryLdap(
        parent_dn, '(&(objectCategory=computer))', scope=ldap_scope).AndReturn(
            [ldap_host])

    self.c.client.UploadPassphrase(
        recovery_guid, recovery_password, metadata).AndReturn(None)

    self.mox.ReplayAll()
    self.c._ProcessHost(ldap_msfve)
    self.mox.VerifyAll()

  def testProcessHostWithInvalidRecoveryGuid(self):
    ldap_host = {
        'distinguishedName': ['CN=Foo,CN=HOSTNAME,...'],
        'msFVE-RecoveryGuid': ['not a byte string'],
    }
    self.assertRaises(
        bitlocker_ad_sync.InvalidRecoveryGuid, self.c._ProcessHost, ldap_host)



if __name__ == '__main__':
  unittest.main()
