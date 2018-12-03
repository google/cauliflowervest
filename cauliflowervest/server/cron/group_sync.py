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

"""Module to sync various groups from external systems into CauliflowerVest."""

import logging
import webapp2

from google.appengine.api import users
from google.appengine.ext import db

from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.models import base




class GroupSync(webapp2.RequestHandler):
  """Webapp handler to sync group membership data."""

  def _GetGroupMembers(self, group):
    """Returns a list of group member email addresses.

    Args:
      group: str, group name to get the members of.
    Returns:
      list of email addresses of members of the group.
    """
    raise NotImplementedError

  def _BatchDatastoreOp(self, op, entities_or_keys, batch_size=25):
    """Performs a batch Datastore operation on a sequence of keys or entities.

    Args:
      op: func, Datastore operation to perform, i.e. db.put or db.delete.
      entities_or_keys: sequence, db.Key or db.Model instances.
      batch_size: int, number of keys or entities to batch per operation.
    """
    for i in xrange(0, len(entities_or_keys), batch_size):
      op(entities_or_keys[i:i + batch_size])

  def _MakeUserEntity(self, email, user_perms):
    """Returns a base.User entity.

    Args:
      email: str, email address of the user.
      user_perms: dict, dict of permission types with lists of db.User
          permissions. i.e. {'filevault_perms': [RETRIEVE, ESCROW]}
    Returns:
      base.User entity.
    """
    u = base.User(key_name=email, user=users.User(email=email))
    for permission_type in permissions.TYPES:
      u.SetPerms(user_perms.get(permission_type, []), permission_type)
    return u

  def _GetGroupMembersAndPermissions(self):
    """Returns a dict of users from settings.GROUPS with desired permissions.

    GROUPS is a dict of permission types, where each type contains a list of
    groups for that given type with a sequence of permissions members of that
    group should have. This function essentially expands the group membership
    and returns a dict of users and the various permissions they have as a
    result of being in one or more of the groups.

    Returns:
      dict like the following:
    {
      'user1@example.com': {'permission_type1': set(['read', 'write'])},
      'user2@example.com': {'permission_type1': set(['read', 'write'])},
      'user3@example.com': {'permission_type1': set(['read', 'write', 'list']),
                            'permission_type2': set(['read', 'write'])},
      }
    """
    group_users = {}

    # Loop over all permission types and all groups, expanding membership
    # and storing each group members permissions in a dict.
    for permission_type, groups in settings.GROUPS.iteritems():
      # Convert all permissions to sets to avoid duplicate permissions.
      groups = [(g, set(p)) for g, p in groups]

      for group, perms in groups:
        for user in self._GetGroupMembers(group):
          # To accomodate for users that exist in multiple groups, insert new
          # users with permissions and set or add permissions to existing users.
          if user not in group_users:
            group_users[user] = {permission_type: perms}
          elif permission_type not in group_users[user]:
            group_users[user][permission_type] = perms
          else:
            group_users[user][permission_type] = (
                group_users[user][permission_type].union(perms))
    return group_users

  @util.CronJob
  def get(self):
    """Get handler to sync groups from external group storage systems."""
    group_users = self._GetGroupMembersAndPermissions()

    # Get all key names from base.User Datastore kind; set() for O(1) lookup.
    local_users = set([k.name() for k in base.User.all(keys_only=True)])

    # Delete any local users that are no longer in any of the groups.
    users_to_delete = [u for u in local_users if u not in group_users]
    keys_to_delete = [
        db.Key.from_path(base.User.__name__, u) for u in users_to_delete]
    if keys_to_delete:
      logging.debug('Deleting users: %s', users_to_delete)
      self._BatchDatastoreOp(db.delete, keys_to_delete)

    # Write all group_users to base.User Datastore kind, overwriting any
    # existing users in case permissions have changed.
    users_to_put = [
        self._MakeUserEntity(u, p) for u, p in group_users.iteritems()]
    self._BatchDatastoreOp(db.put, users_to_put)
