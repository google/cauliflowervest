#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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
"""Tests for util module."""

import os
import stat


import mock

from google.apputils import basetest
from cauliflowervest.client import util


MOUNT_OUTPUT_NOMINAL = """
/dev/disk0s2 on / (hfs, local, journaled)
devfs on /dev (devfs, local, nobrowse)
/dev/disk0s4 on /Volumes/Untitled 2 (hfs, local, journaled)
map -hosts on /net (autofs, nosuid, automounted, nobrowse)
map auto_home on /home (autofs, automounted, nobrowse)
""".strip()
MOUNT_OUTPUT_OUT_OF_ORDER = """
devfs on /dev (devfs, local, nobrowse)
/dev/disk0s4 on /Volumes/Untitled 2 (hfs, local, journaled)
/dev/disk0s2 on / (hfs, local, journaled)
map -hosts on /net (autofs, nosuid, automounted, nobrowse)
map auto_home on /home (autofs, automounted, nobrowse)
""".strip()
MOUNT_OUTPUT_TRAILING_BLANK = """
devfs on /dev (devfs, local, nobrowse)
/dev/disk0s4 on /Volumes/Untitled 2 (hfs, local, journaled)
map -hosts on /net (autofs, nosuid, automounted, nobrowse)
map auto_home on /home (autofs, automounted, nobrowse)

""".lstrip()


class GetRootDiskTest(basetest.TestCase):
  """Test the GetRootDisk() function."""

  @mock.patch.object(util, 'Exec', return_value=(1, '', ''))
  def testEnumerationFailure(self, exec_mock):
    self.assertRaises(util.Error, util.GetRootDisk)

    exec_mock.assert_called_once_with('/sbin/mount')

  @mock.patch.object(util, 'Exec', return_value=(0, MOUNT_OUTPUT_NOMINAL, ''))
  def testOk(self, exec_mock):
    self.assertEquals('/dev/disk0s2', util.GetRootDisk())

    exec_mock.assert_called_once_with('/sbin/mount')

  @mock.patch.object(
      util, 'Exec', return_value=(0, MOUNT_OUTPUT_OUT_OF_ORDER, ''))
  def testOutOfOrder(self, exec_mock):
    self.assertEquals('/dev/disk0s2', util.GetRootDisk())

    exec_mock.assert_called_once_with('/sbin/mount')

  @mock.patch.object(
      util, 'Exec', return_value=(0, MOUNT_OUTPUT_TRAILING_BLANK, ''))
  def testTrailingBlank(self, exec_mock):
    self.assertRaises(util.Error, util.GetRootDisk)

    exec_mock.assert_called_once_with('/sbin/mount')

  @mock.patch.object(util, 'Exec', side_effect=util.ExecError)
  def testException(self, exec_mock):
    self.assertRaises(util.Error, util.GetRootDisk)

    exec_mock.assert_called_once_with('/sbin/mount')


class SafeOpenTest(basetest.TestCase):
  """Test the SafeOpen() function."""
  dir = '/var/root/Library/cauliflowervest'
  path = '/var/root/Library/cauliflowervest/access_token.dat'

  @mock.patch.object(os, 'makedirs', side_effect=OSError)
  def testDirExists(self, makedirs_mock):
    result = object()

    open_mock = mock.Mock()
    open_mock.return_value = result

    self.assertEqual(
        util.SafeOpen(self.path, 'r', open_=open_mock), result)

    open_mock.assert_called_with(self.path, 'r')
    makedirs_mock.assert_called_once_with(self.dir, 0700)

  @mock.patch.object(os, 'mknod', side_effect=OSError)
  @mock.patch.object(os, 'makedirs')
  def testFileExists(self, makedirs_mock, mknod_mock):
    result = object()
    open_mock = mock.Mock()
    open_mock.return_value = result

    self.assertEqual(
        util.SafeOpen(self.path, 'r', open_=open_mock), result)

    open_mock.assert_called_with(self.path, 'r')
    makedirs_mock.assert_called_once_with(self.dir, 0700)
    mknod_mock.assert_called_once_with(self.path, 0600 | stat.S_IFREG)

  @mock.patch.object(os, 'mknod')
  @mock.patch.object(os, 'makedirs')
  def testOk(self, makedirs_mock, mknod_mock):
    result = object()

    open_mock = mock.Mock(return_value=result)

    self.assertEqual(
        util.SafeOpen(self.path, 'r', open_=open_mock), result)

    open_mock.assert_called_with(self.path, 'r')
    makedirs_mock.assert_called_once_with(self.dir, 0700)
    mknod_mock.assert_called_once_with(self.path, 0600 | stat.S_IFREG)


class UtilModuleTest(basetest.TestCase):
  """Test module level functions in util."""

  @mock.patch.object(util.plistlib, 'readPlistFromString', return_value='plist')
  @mock.patch.object(util, 'Exec', return_value=(0, 'stdout', 'stderr'))
  def testGetPlistFromExec(self, exec_mock, read_plist_mock):
    self.assertEqual('plist', util.GetPlistFromExec('cmd', stdin='stdin'))

    exec_mock.assert_called_once_with('cmd', stdin='stdin')
    read_plist_mock.assert_called_once_with('stdout')

  @mock.patch.object(util, 'Exec', return_value=(1, 'stdout', 'stderr'))
  def testGetPlistFromExecNonZeroReturncode(self, exec_mock):
    self.assertRaises(util.ExecError, util.GetPlistFromExec, 'cmd')

    exec_mock.assert_called_once_with('cmd', stdin=None)

  @mock.patch.object(
      util.plistlib, 'readPlistFromString', side_effect=util.expat.ExpatError)
  @mock.patch.object(util, 'Exec', return_value=(0, 'stdout', 'stderr'))
  def testGetPlistFromExecPlistParseError(self, exec_mock, _):
    self.assertRaises(util.ExecError, util.GetPlistFromExec, 'cmd')

    exec_mock.assert_called_once_with('cmd', stdin=None)

  def testJoinURL(self):
    base_url = 'http://example.com'
    part1 = 'foo'
    part2 = 'bar'
    out = util.JoinURL(base_url, part1, part2)
    self.assertEqual(out, 'http://example.com/foo/bar')

  def testJoinURLWithTrailingSlashOnBaseURL(self):
    base_url = 'http://example.com/'
    part1 = 'foo'
    part2 = 'bar'
    out = util.JoinURL(base_url, part1, part2)
    self.assertEqual(out, 'http://example.com/foo/bar')

  def testJoinURLWithLeadingSlashOnInnerURLPart(self):
    base_url = 'http://example.com'
    part1 = '/foo'
    part2 = 'bar'
    out = util.JoinURL(base_url, part1, part2)
    self.assertEqual(out, 'http://example.com/foo/bar')

  def testJoinURLWithLeadingAndTrailingSlashOnInnerURLPart(self):
    base_url = 'http://example.com'
    part1 = '/foo/'
    part2 = '/bar'
    out = util.JoinURL(base_url, part1, part2)
    self.assertEqual(out, 'http://example.com/foo/bar')

  def testJoinURLWithTrailingSlashOnInnerURLPart(self):
    base_url = 'http://example.com'
    part1 = 'foo/'
    part2 = 'bar'
    out = util.JoinURL(base_url, part1, part2)
    self.assertEqual(out, 'http://example.com/foo/bar')

  def testJoinURLWithTrailingSlashOnLastURLPart(self):
    base_url = 'http://example.com'
    part1 = 'foo'
    part2 = 'bar/'
    out = util.JoinURL(base_url, part1, part2)
    self.assertEqual(out, 'http://example.com/foo/bar/')

  @mock.patch.object(util, 'Exec')
  def testRetrieveEntropy(self, exec_mock):
    rc = 0
    stdout = 'HIDIdleTime=100\nWhateverOtherCrap\n'
    stderr = ''
    expected_entropy = 'HIDIdleTime=100'

    exec_mock.return_value = (rc, stdout, stderr)

    self.assertEqual(expected_entropy, util.RetrieveEntropy())

    exec_mock.assert_called_once_with(['/usr/sbin/ioreg', '-l'])

  @mock.patch.object(util, 'Exec')
  def testRetrieveEntropyWhenNoOutputResult(self, exec_mock):
    rc = 0
    stdout = 'CrapThatWontMatchTheRegex\n'
    stderr = ''

    exec_mock.return_value = (rc, stdout, stderr)

    self.assertRaises(util.RetrieveEntropyError, util.RetrieveEntropy)

    exec_mock.assert_called_once_with(['/usr/sbin/ioreg', '-l'])

  @mock.patch.object(util, 'Exec')
  def testRetrieveEntropyWhenErrorIoRegOutput(self, exec_mock):
    rc = 0
    stdout = ''
    stderr = ''

    exec_mock.return_value = (rc, stdout, stderr)

    self.assertRaises(util.RetrieveEntropyError, util.RetrieveEntropy)

    exec_mock.assert_called_once_with(['/usr/sbin/ioreg', '-l'])

  @mock.patch.object(util, 'Exec')
  def testRetrieveEntropyWhenErrorIoRegRc(self, exec_mock):
    rc = 1
    stdout = ''
    stderr = ''

    exec_mock.return_value = (rc, stdout, stderr)

    self.assertRaises(util.RetrieveEntropyError, util.RetrieveEntropy)

    exec_mock.assert_called_once_with(['/usr/sbin/ioreg', '-l'])

  @mock.patch.object(util, 'Exec')
  def testRetrieveEntropyWhenErrorIoRegExec(self, exec_mock):
    rc = 1
    stdout = ''
    stderr = ''

    exec_mock.return_value = (rc, stdout, stderr)

    self.assertRaises(util.RetrieveEntropyError, util.RetrieveEntropy)

    exec_mock.assert_called_once_with(['/usr/sbin/ioreg', '-l'])

  def testSupplyEntropy(self):
    entropy = 'entropy'

    file_mock = mock.Mock(spec=file)
    mock_open = mock.Mock(spec=open)
    mock_open.return_value = file_mock

    util.SupplyEntropy(entropy, open_=mock_open)

    mock_open.assert_called_once_with('/dev/random', 'w')
    file_mock.write.assert_called_once_with(entropy)

  def testSupplyEntropyWhenIOErrorOpen(self):
    entropy = 'entropy'

    mock_open = mock.Mock(spec=open)
    mock_open.side_effect = IOError

    self.assertRaises(
        util.SupplyEntropyError, util.SupplyEntropy, entropy, open_=mock_open)

  def testSupplyEntropyWhenIOErrorWrite(self):
    entropy = 'entropy'

    file_mock = mock.Mock(spec=file)
    file_mock.write.side_effect = IOError
    mock_open = mock.Mock(spec=open)
    mock_open.return_value = file_mock

    self.assertRaises(
        util.SupplyEntropyError, util.SupplyEntropy, entropy, open_=mock_open)

  def testSupplyEntropyWhenIOErrorClose(self):
    entropy = 'entropy'

    file_mock = mock.Mock(spec=file)
    file_mock.close.side_effect = IOError
    mock_open = mock.Mock(spec=open)
    mock_open.return_value = file_mock

    self.assertRaises(
        util.SupplyEntropyError, util.SupplyEntropy, entropy, open_=mock_open)

  def testSupplyEntropyWhenNoneSupplied(self):
    entropy = None
    self.assertRaises(util.SupplyEntropyError, util.SupplyEntropy, entropy)


if __name__ == '__main__':
  basetest.main()
