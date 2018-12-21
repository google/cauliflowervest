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

"""group_sync module tests."""



from absl.testing import absltest
import mock

from cauliflowervest.server import service_factory
from cauliflowervest.server.cron import group_sync
from cauliflowervest.server.models import base


class GroupSyncTest(absltest.TestCase):
  """Test the group_sync.GroupSync class."""

  def setUp(self):
    self.g = group_sync.GroupSync()

  def testBatchDatastoreOp(self):
    batch_size = 2
    mock_op = mock.Mock()
    entities = ['foo', 'bar', 'zoo', 'zee', 'bee', 'sting', 'oddcount']

    self.g._BatchDatastoreOp(mock_op, entities, batch_size=batch_size)

    mock_op.assert_has_calls([
        mock.call(['foo', 'bar']),
        mock.call(['zoo', 'zee']),
        mock.call(['bee', 'sting']),
        mock.call(['oddcount'])])

  @mock.patch.object(base, 'User')
  @mock.patch.object(group_sync.users, 'User')
  def testMakeUserEntity(self, users_user, models_user):
    email = 'foouser@example.com'

    user_perms = {
        'another_permissions_type': 'anything',
        }
    for permission_type in group_sync.permissions.TYPES:
      user_perms[permission_type] = set(['read', 'write'])

    mock_obj = mock.MagicMock()
    users_user.return_value = 'user_obj'
    models_user.return_value = mock_obj

    self.assertEqual(mock_obj, self.g._MakeUserEntity(email, user_perms))

    mock_obj.SetPerms.assert_has_calls(
        [mock.call(user_perms[t], t) for t in group_sync.permissions.TYPES])

  @mock.patch.object(base, 'User')
  @mock.patch.object(group_sync.users, 'User')
  def testMakeUserEntityNoPermissions(self, users_user, models_user):
    email = 'foouser@example.com'
    user_perms = {}
    mock_obj = mock.MagicMock()

    users_user.return_value = 'user_obj'
    models_user.return_value = mock_obj

    self.assertEqual(mock_obj, self.g._MakeUserEntity(email, user_perms))

    calls = []
    for permission_type in group_sync.permissions.TYPES:
      calls.append(mock.call([], permission_type))
    mock_obj.SetPerms.assert_has_calls(calls)

  @mock.patch.object(service_factory, 'GetAccountsService')
  def testGetGroupMembersAndPermissions(self, get_account_service_mock):
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

    arg2res = {'group1': group1, 'group2': group2}
    account_service_mock = get_account_service_mock.return_value
    account_service_mock.GetGroupMembers.side_effect = lambda x: arg2res[x]

    ret = self.g._GetGroupMembersAndPermissions()
    self.assertEqual(expected_return, ret)

  @mock.patch.object(group_sync.db.Key, 'from_path')
  @mock.patch.object(base.User, 'all')
  def testGet(self, all_mock, from_path_mock):
    self.g._BatchDatastoreOp = mock.Mock()
    self.g._GetGroupMembersAndPermissions = mock.Mock()
    self.g._MakeUserEntity = mock.Mock()

    group_users = {
        'u2@example.com': {'type1': set(['read', 'write'])},
        'u3@example.com': {'type1': set(['read', 'write'])},
        'u1@example.com': {'type1': set(['read', 'write', 'list']),
                           'type2': set(['read', 'write'])},
        }

    to_del_user = 'todelete@example.com'

    self.g._GetGroupMembersAndPermissions.return_value = group_users

    mock_key_to_del = mock.MagicMock()
    mock_key_u1 = mock.MagicMock()

    all_mock.return_value = [mock_key_to_del, mock_key_u1]

    mock_key_to_del.name.return_value = to_del_user
    mock_key_u1.name.return_value = 'u1@example.com'

    from_path_mock.return_value = 'todeluserkey'

    to_add = []

    calls = []
    for u, p in group_users.iteritems():
      calls.append((u, p, 'toadd-%s' % u))
      to_add.append('toadd-%s' % u)

    def MatchCallSideEffect(a1, a2):
      for u, p, r in calls:
        if u != a1 or p != a2:
          continue
        return r
      raise ValueError
    self.g._MakeUserEntity.side_effect = MatchCallSideEffect

    self.g.get()

    from_path_mock.assert_called_once_with(
        base.User.__name__, to_del_user)

    self.g._BatchDatastoreOp.assert_has_calls([
        mock.call(group_sync.db.delete, ['todeluserkey']),
        mock.call(group_sync.db.put, to_add)])


if __name__ == '__main__':
  absltest.main()
