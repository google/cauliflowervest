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
