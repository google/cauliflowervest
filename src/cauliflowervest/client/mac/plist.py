#!/usr/bin/env python
# 
# Copyright 2012 Google Inc. All Rights Reserved.
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

"""Stub module for reading plist string XML."""




import plistlib
import xml.parsers.expat


class Error(Exception):
  """Class for domain specific exceptions."""


class ApplePlist(object):
  """Stub class for parsing a plist string."""

  def __init__(self, str_xml):
    self._xml = str_xml
    self.plist = None

  def Parse(self):
    try:
      self.plist = plistlib.readPlistFromString(self._xml)
    except xml.parsers.expat.ExpatError as e:
      raise Error(str(e))

  def GetContents(self):
    return self.plist
