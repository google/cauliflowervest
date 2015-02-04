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

"""Base CauliflowerVestClient class."""



import cookielib
import json
import logging
import time
import urllib
import urllib2


# Because of OSS
# pylint: disable=g-line-too-long

import os
import sys
try:
  import fancy_urllib
except ImportError:
  _path = '%s/gae_client.zip' % os.path.dirname(os.path.realpath(__file__))
  sys.path.insert(0, _path)

import fancy_urllib


from cauliflowervest import settings as base_settings
from cauliflowervest.client import settings
from cauliflowervest.client import util

# Prefix to prevent Cross Site Script Inclusion.
JSON_PREFIX = ")]}',\n"


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


def BuildClientLoginOpener(hostname, credentials):
  """Produce an urllib2 OpenerDirective that's logged in by client login.

  Args:
    hostname: host name for server
    credentials: A tuple of (email, password).

  Note: if necessary, "password" should be an application specific password.

  Returns:
    Tuple of (urllib2.OpenerDirective, cookielib.CookieJar) .
  Raises:
    AuthenticationError: when authentication fails.
  """
  cookiejar = cookielib.CookieJar()
  opener = urllib2.build_opener(
      urllib2.HTTPCookieProcessor(cookiejar),
      fancy_urllib.FancyHTTPSHandler(),
      fancy_urllib.FancyRedirectHandler())
  email, password = credentials

  # Step 1: We get an Auth token from ClientLogin.
  req = fancy_urllib.FancyRequest(
      'https://www.google.com/accounts/ClientLogin',
      urllib.urlencode({
          'accountType': 'HOSTED_OR_GOOGLE',
          'Email': email,
          'Passwd': password,
          'service': 'ah',
          'source': 'cauliflowervest',
          })
      )
  try:
    response = opener.open(req)
  except urllib2.HTTPError, e:
    error_body = e.read()
    # TODO(user): Consider more failure cases.
    if 'Error=BadAuthentication' in error_body:
      raise AuthenticationError('Bad email or password.')
    elif 'Error=CaptchaRequired' in error_body:
      # TODO(user): Provide a link to the page where users can fix this:
      #   https://www.google.com/accounts/DisplayUnlockCaptcha
      raise AuthenticationError(
          'Server responded with captcha request; captchas unsupported.')
    else:
      raise AuthenticationError('Authentication: Could not get service token.')

  try:
    response_body = response.read()
    response_dict = dict(x.split('=') for x in response_body.splitlines() if x)
    assert 'Auth' in response_dict
  except AssertionError:
    raise AuthenticationError('Authentication: Service token missing.')

  # Step 2: We pass that token to App Engine, which responds with a cookie.
  params = {
      'auth': response_dict['Auth'],
      'continue': '',
      }
  req = fancy_urllib.FancyRequest(
      'https://%s/_ah/login?%s' % (hostname, urllib.urlencode(params)))
  try:
    response = opener.open(req)
  except urllib2.HTTPError:
    logging.exception('HTTPError while obtaining cookie from ClientLogin.')
    raise AuthenticationError('Authentication: Could not get cookie.')

  return opener




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
      except urllib2.URLError, e:  # Parent of urllib2.HTTPError.
        # Reraise if HTTP 404.
        if isinstance(e, urllib2.HTTPError) and e.code == 404:
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
    request = fancy_urllib.FancyRequest(
        util.JoinURL(self.escrow_url, volume_uuid, '?only_verify_escrow=1'))
    request.set_ssl_info(ca_certs=self._ca_certs_file)
    try:
      self._RetryRequest(request, 'Verifying escrow')
    except urllib2.HTTPError, e:
      if e.code == 404:
        return False
      else:
        raise RequestError('Failed to verify escrow. HTTP %s' % e.code)
    return True

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
