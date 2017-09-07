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
"""Unit tests for machine_data module."""

import base64
import os



import mock

from google.apputils import basetest

from cauliflowervest.client.mac import machine_data


class MachineDataTest(basetest.TestCase):
  """Test the _MachineData class."""

  def setUp(self):
    super(MachineDataTest, self).setUp()
    self.md = machine_data._MachineData({})

  def tearDown(self):
    super(MachineDataTest, self).tearDown()

  def testGetHDDSerialFromProfile(self):
    mock_hdd_serial = base64.b32encode(os.urandom(20))

    def SetHddSerial():
      self.md._profile['hdd_serial'] = mock_hdd_serial

    with mock.patch.object(self.md, '_FindAll', side_effect=SetHddSerial):
      self.assertEquals(mock_hdd_serial, self.md.GetHDDSerial())

  @mock.patch.object(machine_data, 'SystemConfiguration', autospec=True)
  def testGetHostnameSuccess(self, sys_conf_mock):
    hostname = 'foohostname'

    sys_conf_mock.SCDynamicStoreCopyComputerName.return_value = (
        hostname, 'unused')

    self.assertEqual(hostname, self.md.GetHostname())

  @mock.patch.object(machine_data.socket, 'gethostname')
  @mock.patch.object(machine_data, 'SystemConfiguration', autospec=True)
  def testGetHostnameSysConfigHostnameIsNone(
      self, sys_conf_mock, gethostname_mock):
    hostname = 'foohostname'
    gethostname_mock.return_value = hostname

    sys_conf_mock.SCDynamicStoreCopyComputerName.return_value = (None, 'unused')

    self.assertEqual(hostname, self.md.GetHostname())

    sys_conf_mock.SCDynamicStoreCopyComputerName.assert_called_once_with(
        None, None)

  @mock.patch.object(machine_data.socket, 'gethostname')
  @mock.patch.object(machine_data, 'SystemConfiguration', autospec=True)
  def testGetHostnameUnicodeEncodeError(self, sys_conf_mock, gethostname_mock):
    bad_hostname = '\x23asdfasd\342'
    hostname = 'foohostname'
    gethostname_mock.return_value = hostname

    sys_conf_mock.SCDynamicStoreCopyComputerName.return_value = (
        bad_hostname, 'unused')

    self.assertEqual(hostname, self.md.GetHostname())

    sys_conf_mock.SCDynamicStoreCopyComputerName.assert_called_once_with(
        None, None)

  @mock.patch.object(machine_data.socket, 'gethostname')
  def testGetHostnameSysConfigNone(self, gethostname_mock):
    machine_data.SystemConfiguration = None

    hostname = 'foohostname'
    gethostname_mock.return_value = hostname

    self.assertEqual(hostname, self.md.GetHostname())


if __name__ == '__main__':
  basetest.main()
