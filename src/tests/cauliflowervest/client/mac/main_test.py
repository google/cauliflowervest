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
"""Tests for main module."""


import mock

from google.apputils import basetest

from cauliflowervest.client.mac import main


@mock.patch.object(main.tkinter, 'GuiOauth', autospec=True)
class OauthTest(basetest.TestCase):
  """Test the main() method, when login_type is "oauth2"."""

  @mock.patch.object(
      main.corestorage, 'GetStateAndVolumeIds',
      return_value=(None, ['mock_volume_id'], []))
  def testWithEncryptedVolumes(self, get_state_mock, gui_oauth_mock):
    opts = mock.Mock()
    opts.login_type = 'oauth2'
    opts.oauth2_client_id = 'stub_id'
    opts.oauth2_client_secret = 'stub_secret'
    opts.server_url = 'https://cvest.appspot.com'
    opts.username = 'user'

    main.main(opts)

    get_state_mock.assert_called_once()

    gui_oauth_mock.assert_called_once_with('https://cvest.appspot.com', 'user')
    gui_oauth_mock.return_value.EncryptedVolumePrompt.assert_called_once()

  @mock.patch.object(
      main.corestorage, 'GetStateAndVolumeIds',
      return_value=(None, [], ['mock_volume_id']))
  def testWithoutEncryptedVolumes(self, get_state_mock, gui_oauth_mock):
    opts = mock.Mock()
    opts.login_type = 'oauth2'
    opts.no_welcome = False
    opts.oauth2_client_id = 'stub_id'
    opts.oauth2_client_secret = 'stub_secret'
    opts.server_url = 'https://cvest.appspot.com'
    opts.username = 'user'

    main.main(opts)

    get_state_mock.assert_called_once()

    gui_oauth_mock.assert_called_once_with('https://cvest.appspot.com', 'user')
    gui_oauth_mock.return_value.PlainVolumePrompt.assert_called_once_with(False)




if __name__ == '__main__':
  basetest.main()
