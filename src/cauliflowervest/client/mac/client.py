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



import json
import urllib
import urllib2


# Because of OSS
# pylint: disable-msg=C6310

# Importing this module before appengine_rpc in OSS version is necessary
# because PyObjC does some ugliness with imports that isn't compatible
# with zip package imports.
# pylint: disable-msg=C6203
from cauliflowervest.client.mac import machine_data

from cauliflowervest import settings as base_settings
from cauliflowervest.client import base_client
from cauliflowervest.client import util

# Prefix to prevent Cross Site Script Inclusion.
JSON_PREFIX = ")]}',\n"


# pylint: disable-msg=C6409
Error = base_client.Error
UserAbort = base_client.UserAbort
AuthenticationError = base_client.AuthenticationError
RequestError = base_client.RequestError
MetadataError = base_client.MetadataError


class FileVaultClient(base_client.CauliflowerVestClient):
  """Client to perform FileVault operations."""

  ESCROW_PATH = '/filevault'
  REQUIRED_METADATA = base_settings.FILEVAULT_REQUIRED_PROPERTIES

  def __init__(self, base_url, opener):
    super(FileVaultClient, self).__init__(base_url)
    self.opener = opener

  def RetrievePassphrase(self, volume_uuid):
    """Fetches and returns the FileVault passphrase.

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
    request = base_client.fancy_urllib.FancyRequest(url)
    request.set_ssl_info(ca_certs=self._ca_certs_file)
    try:
      response = self.opener.open(request)
    except urllib2.HTTPError, e:
      raise RequestError('Failed to retrieve passphrase. %s' % str(e))
    content = response.read()
    if content[0:6] != JSON_PREFIX:
      raise RequestError('Expected JSON prefix missing.')
    data = json.loads(content[6:])
    return data['passphrase']

  def _GetMetadata(self):
    """Returns a dict of key/value metadata pairs."""
    return machine_data.Get()