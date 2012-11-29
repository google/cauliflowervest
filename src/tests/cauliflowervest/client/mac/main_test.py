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
# # coding=utf-8
#

"""Tests for main module."""



import unittest

import mox
import stubout

from cauliflowervest.client.mac import main


class MainTest(mox.MoxTestBase):
  """Test the main() method."""

  def setUp(self):
    super(MainTest, self).setUp()
    self.mox = mox.Mox()
    self.mox.StubOutClassWithMocks(main.tkinter, 'GuiClientLogin')
    self.mox.StubOutWithMock(main.corestorage, 'GetStateAndVolumeIds')

  def tearDown(self):
    self.mox.UnsetStubs()

  def testWithEncryptedVolumes(self):
    gui = main.tkinter.GuiClientLogin('https://%s.%s' % (main.base_settings.SUBDOMAIN, main.base_settings.DOMAIN))
    main.corestorage.GetStateAndVolumeIds().AndReturn((
        None, ['mock_volume_id'], []))
    gui.EncryptedVolumePrompt()
    self.mox.ReplayAll()
    main.main()
    self.mox.VerifyAll()

  def testWithoutEncryptedVolumes(self):
    gui = main.tkinter.GuiClientLogin('https://%s.%s' % (main.base_settings.SUBDOMAIN, main.base_settings.DOMAIN))
    main.corestorage.GetStateAndVolumeIds().AndReturn((
        None, [], ['mock_volume_id']))
    gui.PlainVolumePrompt(False)
    self.mox.ReplayAll()
    main.main()
    self.mox.VerifyAll()


if __name__ == '__main__':
  unittest.main()