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
# coding=utf-8
#

"""Unit tests for machine_data module."""



import base64
import os
import unittest
import mox
import stubout

from google.apputils import basetest

from cauliflowervest.client import machine_data


class MachineDataTest(mox.MoxTestBase):
  """Test the _MachineData class."""

  def setUp(self):
    super(MachineDataTest, self).setUp()
    self.mox = mox.Mox()
    self.md = machine_data._MachineData({})
    self.stubs = stubout.StubOutForTesting()

  def tearDown(self):
    self.mox.UnsetStubs()
    self.stubs.UnsetAll()

  def testGetHDDSerialFromProfile(self):
    mock_hdd_serial = base64.b32encode(os.urandom(20))

    def SetHddSerial():
      self.md._profile['hdd_serial'] = mock_hdd_serial

    self.mox.StubOutWithMock(self.md, '_FindAll')
    self.md._FindAll().WithSideEffects(SetHddSerial)

    self.mox.ReplayAll()
    self.assertEquals(mock_hdd_serial, self.md.GetHDDSerial())
    self.mox.VerifyAll()

  def testGetHostnameSuccess(self):
    self.mox.StubOutWithMock(machine_data, 'SystemConfiguration')

    hostname = 'foohostname'
    machine_data.SystemConfiguration.SCDynamicStoreCopyComputerName(
        None, None).AndReturn((hostname, 'unused'))

    self.mox.ReplayAll()
    self.assertEqual(hostname, self.md.GetHostname())
    self.mox.VerifyAll()

  def testGetHostnameSysConfigHostnameIsNone(self):
    self.mox.StubOutWithMock(machine_data, 'SystemConfiguration')
    self.mox.StubOutWithMock(machine_data.socket, 'gethostname')

    hostname = 'foohostname'
    machine_data.SystemConfiguration.SCDynamicStoreCopyComputerName(
        None, None).AndReturn((None, 'unused'))
    machine_data.socket.gethostname().AndReturn(hostname)

    self.mox.ReplayAll()
    self.assertEqual(hostname, self.md.GetHostname())
    self.mox.VerifyAll()

  def testGetHostnameUnicodeEncodeError(self):
    self.mox.StubOutWithMock(machine_data, 'SystemConfiguration')
    self.mox.StubOutWithMock(machine_data.socket, 'gethostname')

    bad_hostname = '\x23asdfasd\342'
    hostname = 'foohostname'
    machine_data.SystemConfiguration.SCDynamicStoreCopyComputerName(
        None, None).AndReturn((bad_hostname, 'unused'))
    machine_data.socket.gethostname().AndReturn(hostname)

    self.mox.ReplayAll()
    self.assertEqual(hostname, self.md.GetHostname())
    self.mox.VerifyAll()

  def testGetHostnameSysConfigNone(self):
    self.mox.StubOutWithMock(machine_data.socket, 'gethostname')

    self.stubs.Set(machine_data, 'SystemConfiguration', None)

    hostname = 'foohostname'
    machine_data.socket.gethostname().AndReturn(hostname)

    self.mox.ReplayAll()
    self.assertEqual(hostname, self.md.GetHostname())
    self.mox.VerifyAll()


if __name__ == '__main__':
  unittest.main()