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

"""Tests for util module."""



import os
import stat
import unittest

import mox
import stubout

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


class GetRootDiskTest(mox.MoxTestBase):
  """Test the GetRootDisk() function."""

  def setUp(self):
    super(GetRootDiskTest, self).setUp()
    self.mox = mox.Mox()

  def tearDown(self):
    self.mox.UnsetStubs()

  def testEnumerationFailure(self):
    self.mox.StubOutWithMock(util, 'Exec')
    util.Exec(('/sbin/mount')).AndReturn((1, '', ''))
    self.mox.ReplayAll()
    self.assertRaises(util.Error, util.GetRootDisk)
    self.mox.VerifyAll()

  def testOk(self):
    self.mox.StubOutWithMock(util, 'Exec')
    util.Exec(('/sbin/mount')).AndReturn((0, MOUNT_OUTPUT_NOMINAL, ''))
    self.mox.ReplayAll()
    self.assertEquals('/dev/disk0s2', util.GetRootDisk())
    self.mox.VerifyAll()

  def testOutOfOrder(self):
    self.mox.StubOutWithMock(util, 'Exec')
    util.Exec(('/sbin/mount')).AndReturn((0, MOUNT_OUTPUT_OUT_OF_ORDER, ''))
    self.mox.ReplayAll()
    self.assertEquals('/dev/disk0s2', util.GetRootDisk())
    self.mox.VerifyAll()

  def testTrailingBlank(self):
    self.mox.StubOutWithMock(util, 'Exec')
    util.Exec(('/sbin/mount')).AndReturn((0, MOUNT_OUTPUT_TRAILING_BLANK, ''))
    self.mox.ReplayAll()
    self.assertRaises(util.Error, util.GetRootDisk)
    self.mox.VerifyAll()

  def testException(self):
    self.mox.StubOutWithMock(util, 'Exec')
    util.Exec(('/sbin/mount')).AndRaise(util.ExecError)
    self.mox.ReplayAll()
    self.assertRaises(util.Error, util.GetRootDisk)
    self.mox.VerifyAll()


class SafeOpenTest(mox.MoxTestBase):
  """Test the SafeOpen() function."""
  dir = '/var/root/Library/cauliflowervest'
  path = '/var/root/Library/cauliflowervest/access_token.dat'

  def setUp(self):
    super(SafeOpenTest, self).setUp()
    self.mox = mox.Mox()

  def tearDown(self):
    self.mox.UnsetStubs()

  def testDirExists(self):
    self.mox.StubOutWithMock(os, 'makedirs')
    os.makedirs(self.dir, 0700).AndRaise(OSError)

    result = object()
    open_ = self.mox.CreateMockAnything()
    open_(self.path, 'r').AndReturn(result)
    mox.Replay(open_)

    self.mox.ReplayAll()
    self.assertEqual(
        util.SafeOpen(self.path, 'r', open_=open_), result)
    self.mox.VerifyAll()
    mox.Verify(open_)

  def testFileExists(self):
    self.mox.StubOutWithMock(os, 'makedirs')
    os.makedirs(self.dir, 0700)
    self.mox.StubOutWithMock(os, 'mknod')
    os.mknod(self.path, 0600 | stat.S_IFREG).AndRaise(OSError)

    result = object()
    open_ = self.mox.CreateMockAnything()
    open_(self.path, 'r').AndReturn(result)
    mox.Replay(open_)

    self.mox.ReplayAll()
    self.assertEqual(
        util.SafeOpen(self.path, 'r', open_=open_), result)
    self.mox.VerifyAll()
    mox.Verify(open_)

  def testOk(self):
    self.mox.StubOutWithMock(os, 'makedirs')
    os.makedirs(self.dir, 0700)
    self.mox.StubOutWithMock(os, 'mknod')
    os.mknod(self.path, 0600 | stat.S_IFREG)

    result = object()
    open_ = self.mox.CreateMockAnything()
    open_(self.path, 'r').AndReturn(result)
    mox.Replay(open_)

    self.mox.ReplayAll()
    self.assertEqual(
        util.SafeOpen(self.path, 'r', open_=open_), result)
    self.mox.VerifyAll()
    mox.Verify(open_)


class UtilModuleTest(mox.MoxTestBase):
  """Test module level functions in util."""

  def setUp(self):
    super(UtilModuleTest, self).setUp()
    self.mox = mox.Mox()

  def tearDown(self):
    self.mox.UnsetStubs()

  def testGetPlistFromExec(self):
    self.mox.StubOutWithMock(util, 'Exec')
    self.mox.StubOutWithMock(util.plistlib, 'readPlistFromString')

    util.Exec('cmd', stdin='stdin').AndReturn((0, 'stdout', 'stderr'))
    util.plistlib.readPlistFromString('stdout').AndReturn('plist')

    self.mox.ReplayAll()
    self.assertEqual('plist', util.GetPlistFromExec('cmd', stdin='stdin'))
    self.mox.VerifyAll()

  def testGetPlistFromExecNonZeroReturncode(self):
    self.mox.StubOutWithMock(util, 'Exec')

    util.Exec('cmd', stdin=None).AndReturn((1, 'stdout', 'stderr'))

    self.mox.ReplayAll()
    self.assertRaises(util.ExecError, util.GetPlistFromExec, 'cmd')
    self.mox.VerifyAll()

  def testGetPlistFromExecPlistParseError(self):
    self.mox.StubOutWithMock(util, 'Exec')
    self.mox.StubOutWithMock(util.plistlib, 'readPlistFromString')

    util.Exec('cmd', stdin=None).AndReturn((0, 'stdout', 'stderr'))
    util.plistlib.readPlistFromString('stdout').AndRaise(util.expat.ExpatError)

    self.mox.ReplayAll()
    self.assertRaises(util.ExecError, util.GetPlistFromExec, 'cmd')
    self.mox.VerifyAll()

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

  def testRetrieveEntropy(self):
    self.mox.StubOutWithMock(util, 'Exec')

    rc = 0
    stdout = 'HIDIdleTime=100\nWhateverOtherCrap\n'
    stderr = ''
    expected_entropy = 'HIDIdleTime=100'

    util.Exec(['/usr/sbin/ioreg', '-l']).AndReturn((rc, stdout, stderr))

    self.mox.ReplayAll()
    self.assertEqual(expected_entropy, util.RetrieveEntropy())
    self.mox.VerifyAll()

  def testRetrieveEntropyWhenNoOutputResult(self):
    self.mox.StubOutWithMock(util, 'Exec')

    rc = 0
    stdout = 'CrapThatWontMatchTheRegex\n'
    stderr = ''

    util.Exec(['/usr/sbin/ioreg', '-l']).AndReturn((rc, stdout, stderr))

    self.mox.ReplayAll()
    self.assertRaises(util.RetrieveEntropyError, util.RetrieveEntropy)
    self.mox.VerifyAll()

  def testRetrieveEntropyWhenErrorIoRegOutput(self):
    self.mox.StubOutWithMock(util, 'Exec')

    rc = 0
    stdout = ''
    stderr = ''

    util.Exec(['/usr/sbin/ioreg', '-l']).AndReturn((rc, stdout, stderr))

    self.mox.ReplayAll()
    self.assertRaises(util.RetrieveEntropyError, util.RetrieveEntropy)
    self.mox.VerifyAll()

  def testRetrieveEntropyWhenErrorIoRegRc(self):
    self.mox.StubOutWithMock(util, 'Exec')

    rc = 1
    stdout = ''
    stderr = ''

    util.Exec(['/usr/sbin/ioreg', '-l']).AndReturn((rc, stdout, stderr))

    self.mox.ReplayAll()
    self.assertRaises(util.RetrieveEntropyError, util.RetrieveEntropy)
    self.mox.VerifyAll()

  def testRetrieveEntropyWhenErrorIoRegExec(self):
    self.mox.StubOutWithMock(util, 'Exec')

    rc = 1
    stdout = ''
    stderr = ''

    util.Exec(['/usr/sbin/ioreg', '-l']).AndRaise(util.ExecError)

    self.mox.ReplayAll()
    self.assertRaises(util.RetrieveEntropyError, util.RetrieveEntropy)
    self.mox.VerifyAll()

  def testSupplyEntropy(self):
    mock_open = self.mox.CreateMockAnything()

    entropy = 'entropy'

    mock_open('/dev/random', 'w').AndReturn(mock_open)
    mock_open.write(entropy).AndReturn(None)
    mock_open.close().AndReturn(None)

    self.mox.ReplayAll()
    util.SupplyEntropy(entropy, open_=mock_open)
    self.mox.VerifyAll()

  def testSupplyEntropyWhenIOErrorOpen(self):
    mock_open = self.mox.CreateMockAnything()

    entropy = 'entropy'

    mock_open('/dev/random', 'w').AndRaise(IOError)

    self.mox.ReplayAll()
    self.assertRaises(
        util.SupplyEntropyError, util.SupplyEntropy, entropy, open_=mock_open)
    self.mox.VerifyAll()

  def testSupplyEntropyWhenIOErrorWrite(self):
    mock_open = self.mox.CreateMockAnything()

    entropy = 'entropy'

    mock_open('/dev/random', 'w').AndReturn(mock_open)
    mock_open.write(entropy).AndRaise(IOError)

    self.mox.ReplayAll()
    self.assertRaises(
        util.SupplyEntropyError, util.SupplyEntropy, entropy, open_=mock_open)
    self.mox.VerifyAll()

  def testSupplyEntropyWhenIOErrorClose(self):
    mock_open = self.mox.CreateMockAnything()

    entropy = 'entropy'

    mock_open('/dev/random', 'w').AndReturn(mock_open)
    mock_open.write(entropy).AndReturn(None)
    mock_open.close().AndRaise(IOError)

    self.mox.ReplayAll()
    self.assertRaises(
        util.SupplyEntropyError, util.SupplyEntropy, entropy, open_=mock_open)
    self.mox.VerifyAll()

  def testSupplyEntropyWhenNoneSupplied(self):
    entropy = None
    self.assertRaises(util.SupplyEntropyError, util.SupplyEntropy, entropy)


if __name__ == '__main__':
  unittest.main()