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

"""CauliflowerVestClient and FileVaultClient."""



import cookielib
import json
import logging
import tempfile
import time
import urllib
import urllib2
import urlparse


# Because of OSS
# pylint: disable-msg=C6310

# Importing this module before appengine_rpc in OSS version is necessary
# because PyObjC does some ugliness with imports that isn't compatible
# with zip package imports.
# pylint: disable-msg=C6203
from cauliflowervest.client import machine_data

import os
import sys
try:
  import google.appengine.tools.appengine_rpc
except ImportError:
  from pkgutil import extend_path as _extend_path
  import google
  _path = '%s/gae_client.zip' % os.path.dirname(os.path.realpath(__file__))
  google.__path__ = _extend_path(['%s/google/' % _path], google.__name__)
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


class DownloadError(Error):
  """There was an error downloaded data from the server."""


class UploadError(Error):
  """There was an error uploading data to the server."""


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
      fancy_urllib.FancyHTTPSHandler())
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
    raise AuthenticationError('Authentication: Could not get cookie.')

  return opener


class CauliflowerVestClient(object):
  """Client to interact with the CauliflowerVest service."""

  # sequence of key names of metadata to require; see GetAndValidateMetadata().
  REQUIRED_METADATA = []

  def __init__(self, base_url):
    self._metadata = None
    self.base_url = base_url
    self.hostname = urlparse.urlparse(base_url)[1]

  def GetAndValidateMetadata(self):
    """Retrieves and validates machine metadata.

    Raises:
      MetadataError: one or more of the REQUIRED_METADATA were not found.
    """
    if not self._metadata:
      self._metadata = machine_data.Get()
    for key in self.REQUIRED_METADATA:
      if not self._metadata.get(key, None):
        raise MetadataError('Required metadata is not found: %s' % key)

  def SetOwner(self, owner):
    if not self._metadata:
      self.GetAndValidateMetadata()
    self._metadata['owner'] = owner


class FileVaultClient(CauliflowerVestClient):
  """Client to perform FileVault operations."""

  FILEVAULT_PATH = '/filevault'
  MAX_TRIES = 5  # Number of times to try an escrow upload.
  REQUIRED_METADATA = base_settings.FILEVAULT_REQUIRED_PROPERTIES
  TRY_DELAY_FACTOR = 5  # Number of seconds, (* try_num), to wait between tries.

  def __init__(self, base_url, opener):
    super(FileVaultClient, self).__init__(base_url)
    self.opener = opener
    self.filevault_url = urlparse.urljoin(base_url, self.FILEVAULT_PATH)

    # Write the ROOT_CA_CERT_CHAIN_PEM to disk, as a tempfile, for fancy_urllib.
    self._ca_certs_tf = tempfile.NamedTemporaryFile()
    self._ca_certs_tf.write(settings.ROOT_CA_CERT_CHAIN_PEM)
    self._ca_certs_tf.flush()
    self._ca_certs_file = self._ca_certs_tf.name

  def VerifyEscrow(self, volume_uuid):
    """Verifies if a Volume UUID has an escrowed FileVault passphrase or not.

    Args:
      volume_uuid: str, Volume UUID to verify escrow for.
    Returns:
      Boolean. True if a passphrase is escrowed, False otherwise.
    Raises:
      DownloadError: there was an error querying the server.
    """
    request = fancy_urllib.FancyRequest(
        util.JoinURL(self.filevault_url, volume_uuid, '?only_verify_escrow=1'))
    request.set_ssl_info(ca_certs=self._ca_certs_file)
    try:
      self.opener.open(request)
    except urllib2.HTTPError, e:
      if e.code == 404:
        return False
      else:
        raise DownloadError('Failed to verify escrow. HTTP %s' % e.code)
    return True

  def RetrievePassphrase(self, volume_uuid):
    """Fetches and returns the FileVault passphrase.

    Args:
      volume_uuid: str, Volume UUID to fetch the keychain for.
    Returns:
      str: passphrase to unlock the keychain.
    Raises:
      DownloadError: there was an error downloading the keychain.
    """
    request = fancy_urllib.FancyRequest(
        util.JoinURL(self.filevault_url, volume_uuid))
    request.set_ssl_info(ca_certs=self._ca_certs_file)
    try:
      response = self.opener.open(request)
    except urllib2.HTTPError, e:
      raise DownloadError('Failed to retrieve passphrase. %s' % str(e))
    content = response.read()
    if content[0:6] != JSON_PREFIX:
      raise DownloadError('Expected JSON prefix missing.')
    data = json.loads(content[6:])
    return data['passphrase']

  def UploadPassphrase(self, volume_uuid, passphrase):
    """Uploads a FileVault volume uuid/passphrase pair with metadata.

    Args:
      volume_uuid: str, UUID of FileVault encrypted volume.
      passphrase: str, passphrase that can be used to unlock the volume.
    Raises:
      UploadError: there was an error uploading to the server.
    """

    # Ugh, urllib2 only does GET and POST?!
    class PutRequest(fancy_urllib.FancyRequest):
      def __init__(self, *args, **kwargs):
        fancy_urllib.FancyRequest.__init__(self, *args, **kwargs)
        self._method = 'PUT'

      def get_method(self):  # pylint: disable-msg=C6409
        return 'PUT'

    if not self._metadata:
      self.GetAndValidateMetadata()
    url = '%s?%s' % (
        util.JoinURL(self.filevault_url, volume_uuid),
        urllib.urlencode(self._metadata))

    for try_num in range(self.MAX_TRIES):
      request = PutRequest(url, data=passphrase)
      request.set_ssl_info(ca_certs=self._ca_certs_file)
      try:
        self.opener.open(request)
        break
      except urllib2.HTTPError, e:
        if try_num == self.MAX_TRIES - 1:
          logging.exception('Uploading passphrase failed permanently.')
          raise UploadError(
              'Uploading passphrase failed permanently: %s', str(e))
        logging.warning(
            'Uploading passphrase failed with HTTP %s. Retrying ...', e.code)
        time.sleep((try_num + 1) * self.TRY_DELAY_FACTOR)