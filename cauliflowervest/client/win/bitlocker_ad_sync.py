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

#!/usr/bin/python2.7

"""Sync BitLocker recovery keys from Active Directory to CauliflowerVest.

Polls msFVE-RecoveryInformation objects from Microsoft Active Directory, using
LDAP, and escrows to CauliflowerVest.

To poll effectively, a loader such as this must use a pointer to find only
objects that have been added or updated since the last execution or load cycle.
Given there are no replicated attributes which can be used as such a pointer,
the loader must always connect to the same Active Directory Domain Controller,
and use one of two options, uSNChanged or whenChanged.

uSNChanged advantages: increments for any and all changes to any and all
  objects on the local domain controller. Thus, searching for uSNChanged > N
  will ensure zero changes are missed.  uSNChanged disadvantages: if a DC is
  down for an extended period of time or indefinitely, changing Domain
  Controllers means either starting with uSNChanged=0, thus importing every
  account. If this need arises, it might be better to manually query the new
  DC to find a uSNChanged number corresponding to local changes a set time
  before loading from the original DC went offline, say the max replication
  time of 90 minutes, to reduce time taken catching up. It is safe to restart
  at 0 it will just take up to several hours for the sync to catch up.

whenChanged advantages: if a DC is down for an extended period of time or
  indefinitely, to switch the loader to a new DC whenChanged can simply be
  tweaked manually, by subtracting the max replication time of 90 minutes,
  which makes for easier DC switching.
whenChanged disadvantages: whenChanged only has second resolution, so it's
  possible even on a healthy DC that queries may miss updates, if cases where
  more than a single object is updated per second.

For more, see http://support.microsoft.com/kb/891995

Therefore, this loader uses the uSNChanged sequence number, as the CauliflowerVest team
feels Domain Controller downtime should be short lived and infrequent.
"""

#  polish credential storage/retrieval for open source.

import datetime
import getpass
import re
import sys
import time
import os
import urllib
import urllib2
import uuid



from absl import app
from absl import flags
from absl import logging
import ldap
from ldap import controls


from cauliflowervest.client import base_client
from cauliflowervest.client.win import client as win_client


BASE_DNS = [
    'OU=Workstations,DC=ad,DC=example,DC=com',
]


INVALID_DN_REGEX = re.compile(r'^$')
MAX_CONNECTION_FAILURES = 4
MAX_QUERY_FAILURES = 3

FLAGS = flags.FLAGS
flags.DEFINE_string(
    'server_hostname',
    'example.appspot.com',
    'Hostname for the CauliflowerVest App Engine server.')
flags.DEFINE_string(
    'ad_user',
    'example_user@ad.example.com',
    'User account to connect to Active Directory with.')
flags.DEFINE_integer(
    'daemon_poll_interval', 300,
    'Maximum daemon poll-for-updates frequency, in seconds.')
flags.DEFINE_string(
    'ldap_url',
    '',
    'LDAP URL to Microsoft Active Directory')
flags.DEFINE_integer(
    'page_size', 50, 'Number of objects to load in each query.')
flags.DEFINE_bool(
    'redact_recovery_passwords', True, 'Redacts recovery passwords, for dev.')
flags.DEFINE_string(
    'usn_changed_file_path',
    '/tmp/usn_changed',
    'Path to store UNS Changed state, to allow for iterative polling.')


class Error(Exception):
  """Class for domain-specific exceptions."""


class InvalidGuid(Error):
  """An invalid GUID value was encountered."""


class InvalidDistinguishedName(Error):
  """An invalid DistinguishedName was encountered."""


class BitLockerAdSync(object):
  """Escrows BitLocker recovery keys in Active Directory to CauliflowerVest."""

  def __init__(
      self, ldap_url=None, auth_user=None, auth_password=None, page_size=50,
      client=None):
    self.auth_user = auth_user
    self.auth_password = auth_password
    self.conn = None
    self.ldap_url = ldap_url
    self.page_size = page_size
    self.client = client


  def _ConnectToAd(self):
    """Establish a connection to the Active Directory server."""

    # To enable verbose debug logging, uncomment the following line.
    # ldap.set_option(ldap.OPT_DEBUG_LEVEL, 255)

    ldap.set_option(ldap.OPT_REFERRALS, 0)
    ldap.set_option(ldap.OPT_X_TLS_ALLOW, 1)

    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
    logging.debug('Connecting to Active Directory: %s', self.ldap_url)

    failures = 0
    while True:
      try:
        self.conn = ldap.initialize(self.ldap_url)
        self.conn.protocol_version = ldap.VERSION3
        self.conn.simple_bind_s(self.auth_user, self.auth_password)
        break
      except ldap.LDAPError, e:
        failures += 1
        if failures == MAX_CONNECTION_FAILURES:
          raise
        logging.exception('LDAPError in ConnectToAd().')
        if e.args and e.args[0].get('desc') == 'Can\'t contact LDAP server':
          time.sleep(5 * failures)
          continue
        raise

  def _DisconnectFromAd(self):
    self.conn.unbind_s()
    self.conn = None

  def _ProcessHost(self, d):
    """Retrieves recovery data from an LDAP host and escrows to CauliflowerVest.

    Args:
      d: a single ldap.conn.result3() result dictionary.
    Raises:
      InvalidDistinguishedName: the given host had an invalid DN.
      InvalidGuid: the given host had an invalid GUID.
    """
    dn = d['distinguishedName'][0]
    # Parse the hostname out of the distinguishedName, which is in this format:
    #   CN=<timestamp>{<recovery_guid>},CN=<hostname>,OU=Workstations,...
    hostname = dn.split(',')[1][len('CN='):]

    # Ignore records with legacy DNs, as they have invalid RecoveryGUIDs,
    # and all have separate valid records.
    if INVALID_DN_REGEX.search(dn):
      raise InvalidDistinguishedName(dn)

    # Some msFVE-RecoveryGuid values may be invalid, so carefully attempt to
    # contruct the recovery_guid, and skip over objects which are invalid.
    try:
      recovery_guid = str(
          uuid.UUID(bytes_le=d['msFVE-RecoveryGuid'][0])).upper()
      volume_guid = str(
          uuid.UUID(bytes_le=d['msFVE-VolumeGuid'][0])).upper()
    except ValueError:
      raise InvalidGuid(
          '%s: %s' % (hostname, d['msFVE-RecoveryGuid']))

    if FLAGS.redact_recovery_passwords:
      recovery_password = '--redacted--'
    else:
      recovery_password = d['msFVE-RecoveryPassword'][0]

    when_created = d['whenCreated'][0]
    try:
      datetime.datetime.strptime(when_created, '%Y%m%d%H%M%S.0Z')
    except ValueError:
      logging.error('Unknown whenCreated format: %r', when_created)
      when_created = ''

    parent_guid = None
    # msFVE-RecoveryObject distinguishedName is in the form of:
    #   CN=<TIMESTAMP>{<UUID>},CN=<HOSTNAME>,DC=example,DC=com
    # where CN=<HOSTNAME>,.* is the parent's distinguishedName.
    # Given that the the msFVE-RecoveryObject is a child of the parent host,
    # split off the child to obtain the parent's DN.
    parent_dn = dn.split(',', 1)[1]
    # Alternatively:  parent_dn = dn.replace('CN=%s,' % d['name'][0], '')
    ldap_filter = '(&(objectCategory=computer))'
    for host in self._QueryLdap(parent_dn, ldap_filter, scope=ldap.SCOPE_BASE):
      parent_guid = str(uuid.UUID(bytes_le=host['objectGUID'][0])).upper()

    metadata = {
        'hostname': hostname,
        'dn': dn,
        'when_created': when_created,
        'parent_guid': parent_guid,
        'recovery_guid': recovery_guid,
    }

    self.client.UploadPassphrase(volume_guid, recovery_password, metadata)
    logging.info('Escrowed recovery password: %r', volume_guid)

  def _QueryLdap(self, base_dn, ldap_filter, scope=ldap.SCOPE_SUBTREE):
    """Yields LDAP results for a given filter in a given base DN.

    This method exists primarily to assist with paging through large result
    sets, and to centralize exception handling and retrying.

    Args:
      base_dn: str base distinguishedName to query within.
      ldap_filter: str LDAP filter to query with.
      scope: ldap.SCOPE_SUBTREE (default), SCOPE_ONELEVEL, or SCOPE_BASE.
    Yields:
      LDAP result dictionary.
    Raises:
      ldap.LDAPError: there was an error querying LDAP.
    """
    if not self.conn:
      self._ConnectToAd()

    page_control = controls.SimplePagedResultsControl(
        True, size=self.page_size, cookie='')

    failures = 0
    # Iterate over all hosts matching the given ldap_filter, in batches of
    # self.page_size, escrowing each resulting recovery object.
    while True:
      server_controls = [page_control]
      query_id = self.conn.search_ext(
          base_dn, scope, ldap_filter, serverctrls=server_controls)

      try:
        _, results, _, server_controls = self.conn.result3(query_id)
      except ldap.LDAPError:
        failures += 1
        if failures == MAX_QUERY_FAILURES:
          raise
        logging.exception('LDAPError on result3() call.')
        time.sleep(5 * failures)
        self._ConnectToAd()
        continue
      else:
        failures = 0

      for result in results:
        yield result[1]

      # Update page_control with server provided control data, otherwise there
      # are no more results, so break.
      cookie = None
      for server_control in server_controls:
        if (server_control.controlType ==
            controls.SimplePagedResultsControl.controlType):
          cookie = server_control.cookie
          if cookie:
            page_control.cookie = cookie
          break
      if not cookie:
        break

  def SyncDn(self, base_dn=None, ldap_filter=None, skip_usn_changed=None):
    """Queries a base DN using an LDAP filter and escrows results to CauliflowerVest.

    Args:
      base_dn: str, base Distinguished Name to load to CauliflowerVest.
      ldap_filter: str, LDAP filter.
      skip_usn_changed: int, uSNChanged number to skip loading.
    Returns:
      Int. The highest uSNChanged number of all loaded hosts.
    """
    top_usn_changed = None

    for result in self._QueryLdap(base_dn, ldap_filter):
      current_usn_changed = int(result['uSNChanged'][0])
      # If the current host was loaded previously, skip it.
      if current_usn_changed == skip_usn_changed:
        continue

      try:
        self._ProcessHost(result)
      except InvalidDistinguishedName as e:
        logging.debug('Skipping object with invalid DN: %r', str(e))
        continue
      except InvalidGuid as e:
        logging.debug(
            'Skipping object with invalid GUID %r', str(e))
        continue

      top_usn_changed = max(top_usn_changed, current_usn_changed)

    self._DisconnectFromAd()

    return top_usn_changed


class UsnChangedState(object):
  """Class to get or set the USN Changed state."""

  def __init__(self):
    self._open = open
    self._exists = os.path.exists

  def Get(self):
    if not self._exists(FLAGS.usn_changed_file_path):
      return 0
    return int(self._open(FLAGS.usn_changed_file_path, 'r').read())

  def Set(self, usn_changed):
    f = self._open(FLAGS.usn_changed_file_path, 'w')
    f.write(str(usn_changed))
    f.close()


def _GetUserAgent():
  return 'BitLockerAdSync'


def _GetAdCredentials():
  ad_user = FLAGS.ad_user
  ad_password = getpass.getpass('Active Directory Password:')
  return ad_user, ad_password


def _GetOpener():
  credentials = base_client.GetOauthCredentials()
  opener = base_client.BuildOauth2Opener(credentials)
  return opener


def _GetLdapUrl():
  ldap_url = FLAGS.ldap_url
  logging.info('using AD: %s', ldap_url)
  if not ldap_url:
    raise ValueError('empty ldap_url')
  return ldap_url


def main(_):

  server_url = 'https://%s' % FLAGS.server_hostname

  headers = {
      'User-agent': _GetUserAgent(),
  }
  ad_user, ad_password = _GetAdCredentials()

  usn_changed_state = UsnChangedState()
  while True:
    opener = _GetOpener()
    client = win_client.BitLockerClient(server_url, opener, headers=headers)
    bitlocker_sync = BitLockerAdSync(
        ldap_url=_GetLdapUrl(), auth_user=ad_user, auth_password=ad_password,
        client=client, page_size=FLAGS.page_size)

    loop_start = time.time()
    last_usn = usn_changed_state.Get()
    ldap_filter = (
        '(&(objectClass=msFVE-RecoveryInformation)(uSNChanged>=%d))' % last_usn)
    logging.info('Querying AD starting with uSNChanged: %r', last_usn)

    top_usn_changed = None
    for base_dn in BASE_DNS:
      current_usn_changed = bitlocker_sync.SyncDn(
          base_dn=base_dn, ldap_filter=ldap_filter, skip_usn_changed=last_usn)
      top_usn_changed = max(top_usn_changed, current_usn_changed)

    if top_usn_changed:
      usn_changed_state.Set(top_usn_changed)

    loop_end = time.time()
    delay = max(0, loop_start - loop_end + FLAGS.daemon_poll_interval)
    logging.info('Cycle end: sleeping for %.2f seconds', delay)
    time.sleep(delay)


if __name__ == '__main__':
  app.run(main)
