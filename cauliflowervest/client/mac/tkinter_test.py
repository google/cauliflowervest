#
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
#
#
"""Tests for main module."""

import unittest



import mock

from cauliflowervest import settings as base_settings
from cauliflowervest.client import base_client
from cauliflowervest.client import settings
from cauliflowervest.client.mac import client
from cauliflowervest.client.mac import tkinter





class _NoGuiOauth(tkinter.GuiOauth):
  """A subclass of GuiOauth which stubs out TK and client interactions."""

  def __init__(self):
    self.server_url = 'http://app.example.com'
    self.client_id = 'stub'
    self.client_secret = 'stub'

  def _ShowLoggingInMessage(self):
    pass


class GuiOauthTest(unittest.TestCase):
  """Test the `GuiOauth` class."""

  def setUp(self):
    super(GuiOauthTest, self).setUp()
    base_settings.OAUTH_CLIENT_ID = 'stub'
    settings.OAUTH_CLIENT_SECRET = 'stub'

  def testAuthenticateFailBadMetadata(self):
    with mock.patch.object(base_client, 'GetOauthCredentials') as _:
      mock_fvc = mock.MagicMock(client.FileVaultClient)
      mock_fvc.GetAndValidateMetadata.side_effect = base_client.MetadataError(
          'missing data')
      with mock.patch.object(client, 'FileVaultClient') as mock_fvc_cls:
        mock_fvc_cls.return_value = mock_fvc
        cb = mock.Mock()
        cb.return_value = None
        _NoGuiOauth()._Authenticate(cb)
        self.assertEqual(1, cb.call_count)
        self.assertEqual('missing data', cb.call_args[0][0])

  def testAuthenticateSuccess(self):
    with mock.patch.object(base_client, 'GetOauthCredentials') as _:
      mock_fvc = mock.MagicMock(client.FileVaultClient)
      mock_fvc.GetAndValidateMetadata.return_value = None
      with mock.patch.object(client, 'FileVaultClient') as mock_fvc_cls:
        mock_fvc_cls.return_value = mock_fvc

        result = _NoGuiOauth()._Authenticate(self.fail)
        self.assertIsInstance(result, base_client.CauliflowerVestClient)


if __name__ == '__main__':
  unittest.main()
