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
##

"""Base CauliflowerVestClient class."""



import json
import logging
import optparse
import time
import urllib
import urllib2


import os
import sys
try:
  import fancy_urllib
except ImportError:
  _path = os.path.dirname(os.path.realpath(__file__))
  _path += '/gae_client.zip'
  sys.path.insert(0, _path)

import fancy_urllib
import oauth2client.client
import oauth2client.tools


from cauliflowervest import settings as base_settings
from cauliflowervest.client import settings
from cauliflowervest.client import util

# Prefix to prevent Cross Site Script Inclusion.
JSON_PREFIX = ")]}',\n"

LOGIN_TYPE_OPTIONS = 'oauth2'

PARSER = optparse.OptionParser()
PARSER.add_option(
    '--debug', dest='debug',
    help='Enable debug mode.',
    action='store_true', default=False)
PARSER.add_option(
    '--login_type', dest='login_type',
    help='Type of login to perform. One of: %s' % LOGIN_TYPE_OPTIONS,
    default='oauth2'
    )
PARSER.add_option(
    '--server_url', dest='server_url',
    help='The URL where CauliflowerVest server is located (scheme + host, no path).',
    default='https://' + base_settings.SERVER_HOSTNAME)
PARSER.add_option(
    '-v', '-V', '--version', action='store_true', dest='version',
    help='Display the version of the CauliflowerVest client.'
    )


class Error(Exception):
  """Class for domain specific exceptions."""


class UserAbort(Error):
  """User aborted process."""


class AuthenticationError(Error):
  """There was an error with authentication."""


class RequestError(Error):
  """There was an error interacting with the server."""


class MetadataError(Error):
  """There was an error with machine metadata."""




class CauliflowerVestClient(object):
  """Client to interact with the CauliflowerVest service."""

  ESCROW_PATH = None  # String path to escrow to, set by subclasses.

  # Sequence of key names of metadata to require; see GetAndValidateMetadata().
  REQUIRED_METADATA = []

  # The metadata key under which the passphrase is stored.
  PASSPHRASE_KEY = 'passphrase'

  MAX_TRIES = 5  # Number of times to try an escrow upload.
  TRY_DELAY_FACTOR = 5  # Number of seconds, (* try_num), to wait between tries.

  XSRF_PATH = '/xsrf-token/%s'

  def __init__(self, base_url, opener, headers=None):
    self._metadata = None
    self.base_url = base_url
    self.xsrf_url = util.JoinURL(base_url, self.XSRF_PATH)
    if self.ESCROW_PATH is None:
      raise ValueError('ESCROW_PATH must be set by CauliflowerVestClient subclasses.')
    self.escrow_url = util.JoinURL(base_url, self.ESCROW_PATH)
    self.opener = opener
    self.headers = headers or {}

    self._ca_certs_file = settings.ROOT_CA_CERT_CHAIN_PEM_FILE_PATH

  def _GetMetadata(self):
    """Returns a dict of key/value metadata pairs."""
    raise NotImplementedError

  def RetrieveSecret(self, volume_uuid):
    """Fetches and returns the passphrase.

    Args:
      volume_uuid: str, Volume UUID to fetch the passphrase for.
    Returns:
      str: passphrase to unlock an encrypted volume.
    Raises:
      RequestError: there was an error downloading the passphrase.
    """
    xsrf_token = self._FetchXsrfToken(base_settings.GET_PASSPHRASE_ACTION)
    url = '%s?%s' % (util.JoinURL(self.escrow_url, volume_uuid),
                     urllib.urlencode({'xsrf-token': xsrf_token}))
    request = fancy_urllib.FancyRequest(url)
    request.set_ssl_info(ca_certs=self._ca_certs_file)
    try:
      response = self.opener.open(request)
    except urllib2.HTTPError, e:
      raise RequestError('Failed to retrieve passphrase. %s' % str(e))
    content = response.read()
    if not content.startswith(JSON_PREFIX):
      raise RequestError('Expected JSON prefix missing.')
    data = json.loads(content[len(JSON_PREFIX):])
    return data[self.PASSPHRASE_KEY]

  def GetAndValidateMetadata(self):
    """Retrieves and validates machine metadata.

    Raises:
      MetadataError: one or more of the REQUIRED_METADATA were not found.
    """
    if not self._metadata:
      self._metadata = self._GetMetadata()
    for key in self.REQUIRED_METADATA:
      if not self._metadata.get(key, None):
        raise MetadataError('Required metadata is not found: %s' % key)

  def SetOwner(self, owner):
    if not self._metadata:
      self.GetAndValidateMetadata()
    self._metadata['owner'] = owner

  def _FetchXsrfToken(self, action):
    request = fancy_urllib.FancyRequest(self.xsrf_url % action)
    request.set_ssl_info(ca_certs=self._ca_certs_file)
    response = self._RetryRequest(request, 'Fetching XSRF token')
    return response.read()

  def _RetryRequest(self, request, description):
    for k, v in self.headers.iteritems():
      request.add_header(k, v)

    for try_num in range(self.MAX_TRIES):
      try:
        return self.opener.open(request)
      except urllib2.URLError as e:  # Parent of urllib2.HTTPError.
        # Reraise if HTTP 4xx.
        if isinstance(e, urllib2.HTTPError) and 400 <= e.code < 500:
          raise
        # Otherwise retry other HTTPError and URLError failures.
        if try_num == self.MAX_TRIES - 1:
          logging.exception('%s failed permanently.', description)
          raise RequestError(
              '%s failed permanently: %%s' % description, str(e))
        logging.warning(
            '%s failed with (%s). Retrying ...', description, str(e))
        time.sleep((try_num + 1) * self.TRY_DELAY_FACTOR)

  def VerifyEscrow(self, volume_uuid):
    """Verifies if a Volume UUID has a passphrase escrowed or not.

    Args:
      volume_uuid: str, Volume UUID to verify escrow for.
    Returns:
      Boolean. True if a passphrase is escrowed, False otherwise.
    Raises:
      RequestError: there was an error querying the server.
    """
    url = util.JoinURL(self.escrow_url, volume_uuid, '?only_verify_escrow=1')
    request = fancy_urllib.FancyRequest(url)
    request.set_ssl_info(ca_certs=self._ca_certs_file)
    try:
      response = self._RetryRequest(request, 'Verifying escrow')
      response_body = response.read()
      return 'Escrow verified' in response_body
    except urllib2.HTTPError, e:
      if e.code == 404:
        return False
      else:
        raise RequestError('Failed to verify escrow. HTTP %s' % e.code)

  def UploadPassphrase(self, volume_uuid, passphrase):
    """Uploads a volume uuid/passphrase pair with metadata.

    Args:
      volume_uuid: str, UUID of an encrypted volume.
      passphrase: str, passphrase that can be used to unlock the volume.
    Raises:
      RequestError: there was an error uploading to the server.
    """
    xsrf_token = self._FetchXsrfToken(base_settings.SET_PASSPHRASE_ACTION)

    # Ugh, urllib2 only does GET and POST?!
    class PutRequest(fancy_urllib.FancyRequest):

      def __init__(self, *args, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers']['Content-Type'] = 'application/octet-stream'
        fancy_urllib.FancyRequest.__init__(self, *args, **kwargs)
        self._method = 'PUT'

      def get_method(self):  # pylint: disable=g-bad-name
        return 'PUT'

    if not self._metadata:
      self.GetAndValidateMetadata()
    self._metadata['xsrf-token'] = xsrf_token
    url = '%s?%s' % (
        util.JoinURL(self.escrow_url, volume_uuid),
        urllib.urlencode(self._metadata))

    request = PutRequest(url, data=passphrase)
    request.set_ssl_info(ca_certs=self._ca_certs_file)
    self._RetryRequest(request, 'Uploading passphrase')




def BuildOauth2Opener(credentials):
  """Produce an OAuth compatible urllib2 OpenerDirective."""
  opener = urllib2.build_opener(
      fancy_urllib.FancyHTTPSHandler,
      fancy_urllib.FancyRedirectHandler)
  h = {}
  credentials.apply(h)
  opener.addheaders = h.items()
  return opener


def GetOauthCredentials():
  """Create an OAuth2 `Credentials` object."""
  if not settings.OAUTH_CLIENT_ID:
    raise RuntimeError('Missing OAUTH_CLIENT_ID setting!')
  if not settings.OAUTH_CLIENT_SECRET:
    raise RuntimeError('Missing OAUTH_CLIENT_SECRET setting!')

  httpd = oauth2client.tools.ClientRedirectServer(
      ('localhost', 0), oauth2client.tools.ClientRedirectHandler)
  httpd.timeout = 60
  flow = oauth2client.client.OAuth2WebServerFlow(
      client_id=settings.OAUTH_CLIENT_ID,
      client_secret=settings.OAUTH_CLIENT_SECRET,
      redirect_uri='http://%s:%s/' % httpd.server_address,
      scope=base_settings.OAUTH_SCOPE,
      )
  authorize_url = flow.step1_get_authorize_url()

  oauth2client.tools.webbrowser.open(authorize_url, new=1, autoraise=True)
  httpd.handle_request()

  if 'error' in httpd.query_params:
    raise RuntimeError('Authentication request was rejected.')

  try:
    credentials = flow.step2_exchange(httpd.query_params)
  except oauth2client.client.FlowExchangeError as e:
    raise RuntimeError('Authentication has failed: %s' % e)
  else:
    logging.info('Authentication successful!')
    return credentials


def main(real_main):
  options, unused_sysv = PARSER.parse_args()

  if options.debug:
    logging.getLogger().setLevel(logging.DEBUG)

  if options.version:
    print 'UNKNOWN'
    return 0

  return real_main(options)
