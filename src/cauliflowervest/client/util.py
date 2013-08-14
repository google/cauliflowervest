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

"""CauliflowerVest client general utility functions."""




import logging
import os
import plistlib
import re
import stat
import subprocess
from xml.parsers import expat


class Error(Exception):
  """Base error."""


class EntropyError(Error):
  """Base for all entropy function errors."""


class RetrieveEntropyError(EntropyError):
  """Error retrieving entropy, source failed."""


class SupplyEntropyError(EntropyError):
  """Error supplying entropy to the system."""


class ExecError(Error):
  """Error Exec()uting a command."""

  def __init__(self, message=None, returncode=None, stderr=None):
    super(ExecError, self).__init__(message)
    self.returncode = returncode
    self.stderr = stderr

  def __unicode__(self):
    output = ['Message=%s' % self.args[0]]
    if self.returncode is not None:
      output.append('Return Code=%s' % self.returncode)
    if self.stderr is not None:
      if type(self.stderr) is unicode:
        output.append('stderr=%s' % self.stderr)
      elif type(self.stderr) is str:
        output.append('stderr=%s' % self.stderr.decode('utf-8'))
    return u', '.join(output)

  def __str__(self):
    return self.__unicode__().encode('utf-8')


def Exec(cmd, stdin=None):
  """Executes a process and returns exit code, stdout, stderr.

  Args:
    cmd: str or sequence, command and optional arguments to execute.
    stdin: str, optional, to send to standard in.
  Returns:
    Tuple. (Integer return code, string standard out, string standard error).
  Raises:
    ExecError: When an error occurs while executing cmd. Exec did not complete.
  """
  shell = isinstance(cmd, basestring)
  logging.debug('Exec(%s, shell=%s)', cmd, shell)
  try:
    p = subprocess.Popen(
        cmd, shell=shell,
        stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  except OSError as e:
    raise ExecError(str(e))
  stdout, stderr = p.communicate(stdin)
  return p.returncode, stdout, stderr


def GetPlistFromExec(cmd, stdin=None):
  """Executes a command and returns a parsed plist from the output.

  Args:
    cmd: str or sequence, command and optional arguments to execute.
    stdin: str, optional, to send to standard in.
  Returns:
    Dict from plistlib.readPlistFromString.
  Raises:
    ExecError: either Exec returned non-0 exit, or parsing stdout plist failed.
  """
  returncode, stdout, stderr = Exec(cmd, stdin=stdin)
  if returncode != 0:
    raise ExecError('Exec returned non-zero exit', returncode, stderr)

  try:
    return plistlib.readPlistFromString(stdout)
  except expat.ExpatError as e:
    raise ExecError('Failed to parse plist: %s' % str(e))


def GetRootDisk():
  """Returns the device name of the root disk.

  Returns:
    str, like "/dev/disk...."
  Raises:
    Error: When the root disk could not be found.
  """
  try:
    returncode, stdout, _ = Exec(('/sbin/mount'))
  except ExecError:
    returncode = 'ExecError'

  if returncode != 0:
    raise Error(
        'Could not enumerate mounted disks, mount exit status %s' % returncode)

  for line in stdout.splitlines():
    try:
      device, _, mount_point, _ = line.split(' ', 3)
      if mount_point == '/' and re.search(r'^[/a-z0-9]+$', device, re.I):
        return device
    except ValueError:
      pass

  raise Error('Could not find root disk.')


def JoinURL(base_url, *args):
  """Join two or more parts of a URL.

  Args:
    base_url: str, base URL like https://example.com/foo.
    *args: str arguments to join to the base URL, like 'bar' or '/bar'.
  Returns:
    String URL joined sanely with single slashes separating URL parts.
  """
  url = base_url
  for part in args:
    if part.startswith('/'):
      part = part[1:]

    if not url or url.endswith('/'):
      url +=  part
    else:
      url += '/' + part
  return url


def SafeOpen(path, mode, open_=open):
  """Opens a file, guaranteeing that its directory exists, and makes it 0600.

  Args:
    path: str, path to the file to open, just like open().
    mode: str, open mode to perform, just like open().
    open_: callable, dependency injection for tests only.
  Returns:
    A handle to the open file, just like open().
  """
  try:
    os.makedirs(os.path.dirname(path), 0700)
    os.mknod(path, 0600 | stat.S_IFREG)
  except OSError:
    # File exists.
    pass

  return open_(path, mode)


def RetrieveEntropy():
  """Retrieve entropy bytes from a trusted source and return them as a str.

  Raises:
    RetrieveEntropyError: when the operations to retrieve entropy data from
       the system fail.
  Returns:
    String.
  """
  try:
    rc, stdout, _ = Exec(['/usr/sbin/ioreg', '-l'])
  except ExecError:
    raise RetrieveEntropyError('/usr/sbin/ioreg not executable')

  if rc != 0:
    raise RetrieveEntropyError('ioreg exit status %s' % rc)
  if not stdout:
    raise RetrieveEntropyError('ioreg no or insufficient stdout')

  interesting_lines_re = re.compile(
      '(HIDIdleTime|IODeviceMemory|sessionID|DriverPMAssertionsDetailed|'
      'TimeSinceDeviceIdle|Statistics|IdleTimerPeriod|IOKitDiagnostics|'
      'IOPowerManagement|IOPowerManagement|acpi-mmcfg-seg0|clock-frequency|'
      'pwm-info|HIDPointerAccelerationTable|HIDScrollAccelerationTable|'
      'frequency)')

  output = []
  for l in stdout.splitlines():
    if interesting_lines_re.search(l):
      l = l.strip()
      output.append(l)

  output = ''.join(output)

  if not output:
    raise RetrieveEntropyError('ioreg unexpected output yieled no entropy')

  return output


def SupplyEntropy(entropy, open_=open):
  """Supply entropy to the system RNG.

  Args:
    entropy: str, some string of bytes.
    open_: optional, default open, function with open-like interface
  Raises:
    SupplyEntropyError: when the operations to supply entropy to the system
       fail.
  """
  if not entropy:
    raise SupplyEntropyError('no entropy supplied')

  try:
    f = open_('/dev/random', 'w')
    f.write(entropy)
    f.close()
  except IOError as e:
    raise SupplyEntropyError(str(e))


def UuidIsValid(uuid):
  """Return boolean; true means the UUID is a valid format."""
  return re.search(r'^[\w\d_\.-]+$', uuid, re.I)