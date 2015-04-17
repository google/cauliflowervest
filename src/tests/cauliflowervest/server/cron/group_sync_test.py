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
"""group_sync module tests."""



import mox
import stubout


from google.apputils import app
from google.apputils import basetest
from cauliflowervest.server.cron import group_sync


class GroupSyncTest(mox.MoxTestBase):
  """Test the group_sync.GroupSync class."""

  def setUp(self):
    mox.MoxTestBase.setUp(self)
    self.stubs = stubout.StubOutForTesting()
    self.g = group_sync.GroupSync()

  def tearDown(self):
    self.mox.UnsetStubs()
    self.stubs.UnsetAll()


  def testBatchDatastoreOp(self):
    batch_size = 2
    mock_op = self.mox.CreateMockAnything()
    entities = ['foo', 'bar', 'zoo', 'zee', 'bee', 'sting', 'oddcount']

    mock_op(['foo', 'bar']).AndReturn(None)
    mock_op(['zoo', 'zee']).AndReturn(None)
    mock_op(['bee', 'sting']).AndReturn(None)
    mock_op(['oddcount']).AndReturn(None)

    self.mox.ReplayAll()
    self.g._BatchDatastoreOp(mock_op, entities, batch_size=batch_size)
    self.mox.VerifyAll()

  def testMakeUserEntity(self):
    self.mox.StubOutWithMock(group_sync.models, 'User', True)
    self.mox.StubOutWithMock(group_sync.users, 'User', True)

    email = 'foouser@example.com'

    user_perms = {
        'another_permissions_type': 'anything',
        }
    for permission_type in group_sync.permissions.TYPES:
      user_perms[permission_type] = set(['read', 'write'])

    mock_obj = self.mox.CreateMockAnything()
    group_sync.users.User(email=email).AndReturn('user_obj')
    group_sync.models.User(key_name=email, user='user_obj').AndReturn(mock_obj)

    for permission_type in group_sync.permissions.TYPES:
      mock_obj.SetPerms(user_perms[permission_type], permission_type).AndReturn(
          None)

    self.mox.ReplayAll()
    self.assertEqual(mock_obj, self.g._MakeUserEntity(email, user_perms))
    self.mox.VerifyAll()

  def testMakeUserEntityNoPermissions(self):
    self.mox.StubOutWithMock(group_sync.models, 'User', True)
    self.mox.StubOutWithMock(group_sync.users, 'User', True)

    email = 'foouser@example.com'
    user_perms = {}
    mock_obj = self.mox.CreateMockAnything()
    group_sync.users.User(email=email).AndReturn('user_obj')
    group_sync.models.User(key_name=email, user='user_obj').AndReturn(mock_obj)
    for permission_type in group_sync.permissions.TYPES:
      mock_obj.SetPerms([], permission_type).AndReturn(None)

    self.mox.ReplayAll()
    self.assertEqual(mock_obj, self.g._MakeUserEntity(email, user_perms))
    self.mox.VerifyAll()

  def testGetGroupMembersAndPermissions(self):
    group_sync.settings.GROUPS = {
        'type1': [
            ('group1', ('read', 'write')),
            ('group2', ('read', 'write', 'list')),
            ],
        'type2': [
            ('group2', ('read', 'write')),
            ],
        }

    group1 = ['u1@example.com', 'u2@example.com', 'u3@example.com']
    group2 = ['u1@example.com']

    expected_return = {
        'u2@example.com': {'type1': set(['read', 'write'])},
        'u3@example.com': {'type1': set(['read', 'write'])},
        'u1@example.com': {'type1': set(['read', 'write', 'list']),
                           'type2': set(['read', 'write'])},
        }

    self.mox.StubOutWithMock(self.g, '_GetGroupMembers')
    self.g._GetGroupMembers('group1').InAnyOrder().AndReturn(group1)
    self.g._GetGroupMembers('group2').InAnyOrder().AndReturn(group2)
    self.g._GetGroupMembers('group2').InAnyOrder().AndReturn(group2)

    self.mox.ReplayAll()
    ret = self.g._GetGroupMembersAndPermissions()
    self.assertEqual(ret, expected_return)
    self.mox.VerifyAll()

  def testGet(self):
    self.mox.StubOutWithMock(self.g, '_GetGroupMembersAndPermissions')
    self.mox.StubOutWithMock(self.g, '_BatchDatastoreOp')
    self.mox.StubOutWithMock(self.g, '_MakeUserEntity')
    self.mox.StubOutWithMock(group_sync.models.User, 'all')
    self.mox.StubOutWithMock(group_sync.db.Key, 'from_path')

    group_users = {
        'u2@example.com': {'type1': set(['read', 'write'])},
        'u3@example.com': {'type1': set(['read', 'write'])},
        'u1@example.com': {'type1': set(['read', 'write', 'list']),
                           'type2': set(['read', 'write'])},
        }

    to_del_user = 'todelete@example.com'

    self.g._GetGroupMembersAndPermissions().AndReturn(group_users)

    mock_key_to_del = self.mox.CreateMockAnything()
    mock_key_u1 = self.mox.CreateMockAnything()
    group_sync.models.User.all(keys_only=True).AndReturn(
        [mock_key_to_del, mock_key_u1])
    mock_key_to_del.name().AndReturn(to_del_user)
    mock_key_u1.name().AndReturn('u1@example.com')

    group_sync.db.Key.from_path(
        group_sync.models.User.__name__, to_del_user).AndReturn('todeluserkey')
    self.g._BatchDatastoreOp(group_sync.db.delete, ['todeluserkey']).AndReturn(
        None)

    to_add = []
    for u, p in group_users.iteritems():
      self.g._MakeUserEntity(u, p).InAnyOrder().AndReturn('toadd-%s' % u)
      to_add.append('toadd-%s' % u)
    self.g._BatchDatastoreOp(group_sync.db.put, to_add)

    self.mox.ReplayAll()
    self.g.get()
    self.mox.VerifyAll()


def main(unused_argv):
  basetest.main()


if __name__ == '__main__':
  app.run()
