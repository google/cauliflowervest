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
#
#

"""Tests for main module."""



import unittest


import mox
import stubout

from cauliflowervest.client.mac import main


class OauthTest(mox.MoxTestBase):
  """Test the main() method, when login_type is "oauth2"."""

  def testWithEncryptedVolumes(self):
    self.mox.StubOutClassWithMocks(main.tkinter, 'GuiOauth')
    gui = main.tkinter.GuiOauth('https://cvest.appspot.com', 'user')
    gui.EncryptedVolumePrompt()

    self.mox.StubOutWithMock(main.corestorage, 'GetStateAndVolumeIds')
    main.corestorage.GetStateAndVolumeIds().AndReturn((
        None, ['mock_volume_id'], []))

    opts = mox.MockAnything()
    opts.login_type = 'oauth2'
    opts.oauth2_client_id = 'stub_id'
    opts.oauth2_client_secret = 'stub_secret'
    opts.server_url = 'https://cvest.appspot.com'
    opts.username = 'user'

    self.mox.ReplayAll()
    main.main(opts)
    self.mox.VerifyAll()

  def testWithoutEncryptedVolumes(self):
    self.mox.StubOutClassWithMocks(main.tkinter, 'GuiOauth')
    gui = main.tkinter.GuiOauth('https://cvest.appspot.com', 'user')
    gui.PlainVolumePrompt(False)

    self.mox.StubOutWithMock(main.corestorage, 'GetStateAndVolumeIds')
    main.corestorage.GetStateAndVolumeIds().AndReturn((
        None, [], ['mock_volume_id']))

    opts = mox.MockAnything()
    opts.login_type = 'oauth2'
    opts.no_welcome = False
    opts.oauth2_client_id = 'stub_id'
    opts.oauth2_client_secret = 'stub_secret'
    opts.server_url = 'https://cvest.appspot.com'
    opts.username = 'user'

    self.mox.ReplayAll()
    main.main(opts)
    self.mox.VerifyAll()




if __name__ == '__main__':
  unittest.main()
