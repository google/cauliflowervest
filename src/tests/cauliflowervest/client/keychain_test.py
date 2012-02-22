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

"""Tests for main module."""



import base64
import unittest

import mox
import stubout

from cauliflowervest.client import keychain
from cauliflowervest.client import util


class CreateTest(mox.MoxTestBase):
  """Test the core storage related features."""

  def setUp(self):
    super(CreateTest, self).setUp()
    self.mox = mox.Mox()

  def tearDown(self):
    self.mox.UnsetStubs()

  def testOk(self):
    mock_passphrase = 'random keychain passphrase'
    mock_full_keychain = self.mox.CreateMockAnything()
    mock_full_keychain_file = self.mox.CreateMockAnything()
    mock_pub_keychain = self.mox.CreateMockAnything()
    mock_pub_keychain_file = self.mox.CreateMockAnything()
    open_ = self.mox.CreateMockAnything()

    self.mox.StubOutWithMock(base64, 'b32encode')
    self.mox.StubOutWithMock(util, 'Exec')
    self.mox.StubOutWithMock(keychain, 'Remove')

    base64.b32encode(mox.IsA(basestring)).AndReturn(mock_passphrase)
    util.Exec(mox.In('/usr/bin/certtool'), mox.IsA(basestring)).AndReturn(
        (0, '', ''))
    open_(mox.IsA(basestring), 'r').AndReturn(mock_full_keychain_file)
    mock_full_keychain_file.read().AndReturn(mock_full_keychain)
    keychain.Remove()
    util.Exec(mox.In('/usr/bin/security')).AndReturn(
        (0, '', ''))
    util.Exec(mox.In('/usr/bin/certtool')).AndReturn(
        (0, '', ''))

    open_(mox.IsA(basestring), 'r').AndReturn(mock_pub_keychain_file)
    mock_pub_keychain_file.read().AndReturn(mock_pub_keychain)

    mox.Replay(open_)
    self.mox.ReplayAll()
    self.assertEquals(
        (mock_pub_keychain, mock_full_keychain, mock_passphrase),
        keychain.Create(open_=open_))
    self.mox.VerifyAll()
    mox.Verify(open_)


class RemoveTest(mox.MoxTestBase):
  """Test the Remove() method."""

  def setUp(self):
    super(RemoveTest, self).setUp()
    self.mox = mox.Mox()

  def tearDown(self):
    self.mox.UnsetStubs()

  def testNotExist(self):
    self.mox.StubOutWithMock(util, 'Exec')
    util.Exec(mox.In('/usr/bin/security')).AndReturn((50, '', ''))
    self.mox.ReplayAll()
    keychain.Remove()
    self.mox.VerifyAll()

  def testOk(self):
    self.mox.StubOutWithMock(util, 'Exec')
    util.Exec(mox.In('/usr/bin/security')).AndReturn((0, '', ''))
    self.mox.ReplayAll()
    keychain.Remove()
    self.mox.VerifyAll()

  def testPermissionDenied(self):
    self.mox.StubOutWithMock(util, 'Exec')
    util.Exec(mox.In('/usr/bin/security')).AndReturn((173, '', ''))
    self.mox.ReplayAll()
    self.assertRaises(AssertionError, keychain.Remove)
    self.mox.VerifyAll()


if __name__ == '__main__':
  unittest.main()