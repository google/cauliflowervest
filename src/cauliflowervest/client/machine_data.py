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

"""Module to gather metadata about the machine to be encrypted."""



import socket
try:
  # pylint: disable-msg=C6204,F0401
  import SystemConfiguration  # PyObj-C only.
except ImportError:
  SystemConfiguration = None

# pylint: disable-msg=C6204
from cauliflowervest.client import hw


class _MachineData(hw.SystemProfile):
  def __init__(self, system_profile=None, **kwargs):
    super(_MachineData, self).__init__(**kwargs)
    if system_profile is None:
      self._GetSystemProfile()
    else:
      self._system_profile = system_profile
    self._have_found_all = False

  def _FindAll(self):
    if self._have_found_all: return
    self._have_found_all = True
    super(_MachineData, self)._FindAll()

  def GetHDDSerial(self):
    self._FindAll()
    return self._profile.get('hdd_serial')

  def GetHostname(self):
    host = None
    if SystemConfiguration:
      # NOTE: SCDynamicStoreCopyComputerName returns a unicode object, which
      #   may contain non-utf-8 characters.  We attempt to encode to UTF-8.
      try:
        host, _ = SystemConfiguration.SCDynamicStoreCopyComputerName(None, None)
        host = host.encode('utf-8')
      except UnicodeEncodeError:
        host = None
    if not host:
      host = socket.gethostname()
    return host

  def GetPlatformUUID(self):
    self._FindAll()
    return self._profile.get('platform_uuid')

  def GetSerial(self):
    self._FindAll()
    return self._profile.get('serial_number')


def Get():
  """Get a dictionary of all metadata this module knows how to find."""
  machine_data = _MachineData(
      include_only=['system', 'hardware', 'parallelata', 'serialata'])
  return {
      'hdd_serial': machine_data.GetHDDSerial(),
      'hostname': machine_data.GetHostname(),
      'platform_uuid': machine_data.GetPlatformUUID(),
      'serial': machine_data.GetSerial(),
      }