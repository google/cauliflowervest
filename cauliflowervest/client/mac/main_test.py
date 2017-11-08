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

"""Tests for main module."""

import sys



import mock

from absl import app
from absl.testing import absltest

from cauliflowervest.client.mac import main


@mock.patch.object(sys, 'exit')
@mock.patch.object(main.tkinter, 'GuiOauth', autospec=True)
class OauthTest(absltest.TestCase):
  """Test the main() method, when login_type is "oauth2"."""

  @mock.patch.object(
      main.glue.corestorage.CoreStorage, 'GetStateAndVolumeIds',
      return_value=(None, ['mock_volume_id'], []))
  def testWithEncryptedVolumes(self, get_state_mock, gui_oauth_mock, _):
    argv = [
        'main_test', '--login_type', 'oauth2',
        '--server_url', 'https://cvest.appspot.com',
        '--username', 'user'
    ]

    app.run(main.main, argv=argv)

    get_state_mock.assert_called_once()

    gui_oauth_mock.assert_called_once_with('https://cvest.appspot.com', 'user')
    gui_oauth_mock.return_value.EncryptedVolumePrompt.assert_called_once()

  @mock.patch.object(
      main.glue.corestorage.CoreStorage, 'GetStateAndVolumeIds',
      return_value=(None, [], ['mock_volume_id']))
  def testWithoutEncryptedVolumes(self, get_state_mock, gui_oauth_mock, _):
    argv = [
        'main_test', '--login_type', 'oauth2', '--nowelcome',
        '--server_url', 'https://cvest.appspot.com',
        '--username', 'user'
    ]

    app.run(main.main, argv=argv)

    get_state_mock.assert_called_once()

    gui_oauth_mock.assert_called_once_with('https://cvest.appspot.com', 'user')
    gui_oauth_mock.return_value.PlainVolumePrompt.assert_called_once_with(
        False, status_callback=main.status_callback)




if __name__ == '__main__':
  absltest.main()
