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

"""App Engine Models for CauliflowerVest web application."""

import hashlib
import logging
import traceback



import webapp2

from google.appengine.api import memcache
from google.appengine.api import oauth
from google.appengine.api import users
from google.appengine.ext import db

from cauliflowervest import settings as base_settings
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server.models import errors


VOLUME_ACCESS_HANDLER = 'VolumeAccessHandler'
XSRF_TOKEN_GENERATE_HANDLER = 'XsrfTokenGenerateHandler'




def _GetApiUser():
  """Get the GAE `User` object for the currently authenticated user."""
  user = users.get_current_user()
  if user: return user

  # Note (http://goo.gl/PCgGNp): "On the local development server,
  # oauth.get_current_user() always returns a User object with email set
  # to "example@example.com" and user ID set to 0 regardless of whether or
  # not a valid OAuth request was made.  So test for oauth last.
  try:
    # Get the db.User that represents the user on whose behalf the
    # consumer is making this request.
    user = oauth.get_current_user(base_settings.OAUTH_SCOPE)
    client_id = oauth.get_client_id(base_settings.OAUTH_SCOPE)
    if user and client_id and base_settings.OAUTH_CLIENT_ID == client_id:
      return user
  except oauth.OAuthRequestError:
    pass

  raise errors.AccessDeniedError('All authentication methods failed')


# Here so that AutoUpdatingUserProperty will work without dependency cycles.
def GetCurrentUser():
  """Returns a models.User object for the currently logged in user.

  If the current logged in user is an App Engine admin, a User entity will
  be created for them with permissions.SET_REGULAR permissions and saved to the
  datastore.

  Returns:
    models.User object.
  Raises:
    AccessDeniedError: raised when no user is logged in.
  """
  user = _GetApiUser()

  user_entity = User.get_by_key_name(user.email())
  if not user_entity:
    user_entity = User(key_name=user.email(), user=user)
    if users.is_current_user_admin():
      # Automatically create User entities with full permissions for
      # users with admin privileges.
      for permission_type in permissions.TYPES:
        user_entity.SetPerms(permissions.SET_REGULAR, permission_type)
      user_entity.user = users.User(user.email())
      user_entity.put()

  return user_entity


class AutoUpdatingUserProperty(db.UserProperty):
  """UserProperty that sets the current users.User if not already set."""

  def default_value(self):
    """Returns the current user logged in."""
    try:
      user = GetCurrentUser()
      return user.user  # Store the underlying users.User object.
    except errors.AccessDeniedError:
      pass

    return self.default


class OwnersProperty(db.StringListProperty):
  """Property to store emails."""

  def _Normalize(self, value):
    if not value:
      return value

    if '@' not in value:
      value = '%s@%s' % (value, settings.DEFAULT_EMAIL_DOMAIN)
    return value

  def validate(self, value):
    value = super(OwnersProperty, self).validate(value)
    return [self._Normalize(v) for v in value]


class BasePassphrase(db.Model):
  """Base model for various types of passphrases."""

  def __init__(self, owner=None, **kwds):
    super(BasePassphrase, self).__init__(**kwds)
    if owner:
      assert 'owners' not in kwds
      self.owners = [owner]

  AUDIT_LOG_MODEL = None
  ESCROW_TYPE_NAME = 'base_target'
  TARGET_PROPERTY_NAME = None
  SECRET_PROPERTY_NAME = 'undefined'
  ALLOW_OWNER_CHANGE = False
  MUTABLE_PROPERTIES = [
      'force_rekeying', 'hostname', 'owners',
  ]

  # True for only the most recently escrowed, unique target_id.
  active = db.BooleanProperty(default=True)

  created = db.DateTimeProperty(auto_now_add=True)
  created_by = AutoUpdatingUserProperty()  # user that created the object.
  force_rekeying = db.BooleanProperty(default=False)
  hostname = db.StringProperty()

  def _GetOwner(self):
    if self.owners:
      return self.owners[0]
    return ''

  def _SetOwner(self, new_owner):
    logging.warning('avoid owner property')
    traceback.print_stack()
    self.owners = [new_owner]

  owner = property(_GetOwner, _SetOwner)
  owners = OwnersProperty()

  tag = db.StringProperty(default='default')  # Key Slot

  def ChangeOwners(self, new_owners):
    """Changes owner.

    Args:
      new_owners: list New owners.
    Returns:
      bool whether change was made.
    """
    if self.owners == sorted(new_owners):
      return False
    logging.info('changes owners of %s from %s to %s',
                 self.target_id, self.owners, new_owners)
    self.AUDIT_LOG_MODEL.Log(
        message='changes owners of %s from %s to %s' % (
            self.target_id, self.owners, new_owners))

    self._UpdateMutableProperties(self.key(), {
        'owners': new_owners,
        'force_rekeying': True,
    })
    return True

  def __eq__(self, other):
    for p in self.properties():
      if getattr(self, p) != getattr(other, p):
        return False
    return True

  def __ne__(self, other):
    return not self.__eq__(other)

  def ToDict(self, skip_secret=False):
    passphrase = {p: unicode(getattr(self, p)) for p in self.properties()
                  if not skip_secret or p != self.SECRET_PROPERTY_NAME}
    passphrase['id'] = str(self.key())
    passphrase['active'] = self.active  # store the bool, not string, value
    passphrase['target_id'] = self.target_id
    passphrase['owners'] = self.owners
    return passphrase

  @classmethod
  def GetLatestForTarget(cls, target_id, tag='default'):
    entity = cls.all().filter('tag =', tag).filter(
        '%s =' % cls.TARGET_PROPERTY_NAME, target_id).order('-created').fetch(1)
    if not entity:
      return None
    return entity[0]

  def Clone(self):
    items = {p.name: getattr(self, p.name) for p in self.properties().values()
             if not isinstance(p, db.ComputedProperty)}
    del items['created_by']
    del items['created']
    return self.__class__(**items)

  @db.transactional(xg=True)
  def _PutNew(self, ancestor_key, *args, **kwargs):
    ancestor = self.get(ancestor_key)
    if not ancestor.active:
      raise self.ACCESS_ERR_CLS(
          'parent entity is inactive: %s.' % self.target_id)
    ancestor.active = False
    super(BasePassphrase, ancestor).put(*args, **kwargs)
    return super(BasePassphrase, self).put(*args, **kwargs)

  def put(self, parent=None, *args, **kwargs):  # pylint: disable=g-bad-name
    """Disallow updating an existing entity, and enforce key_name.

    Args:
      parent: Optional. A Passphrase of the same type as the current instance.
        If passed then it is used as the parent entity for this instance.
      *args: Positional arguments to be passed to parent class' put method.
      **kwargs: Keyword arguments to be passed to parent class' put method.
    Returns:
      The key of the instance (either the existing key or a new key).
    Raises:
      errors.DuplicateEntity: Entity is a duplicate of active passphrase with
                       same target_id.
      AccessError: required property was empty or not set.
    """
    if self.hostname:
      self.hostname = self.NormalizeHostname(self.hostname)

    model_name = self.__class__.__name__
    for prop_name in self.REQUIRED_PROPERTIES:
      if not getattr(self, prop_name, None):
        raise self.ACCESS_ERR_CLS('Required property empty: %s' % prop_name)

    if not self.active:
      raise self.ACCESS_ERR_CLS(
          'New entity is not active: %s' % self.target_id)

    if self.has_key():
      raise self.ACCESS_ERR_CLS(
          'Key should be auto genenrated for %s.' % model_name)

    existing_entity = parent
    if not existing_entity:
      existing_entity = self.__class__.GetLatestForTarget(
          self.target_id, tag=self.tag)
    if existing_entity:
      if not existing_entity.active:
        raise self.ACCESS_ERR_CLS(
            'parent entity is inactive: %s.' % self.target_id)
      different_properties = []
      for prop in self.properties():
        if getattr(self, prop) != getattr(existing_entity, prop):
          different_properties.append(prop)

      if not different_properties or different_properties == ['created']:
        raise errors.DuplicateEntity()

      if self.created > existing_entity.created:
        return self._PutNew(existing_entity.key())
      else:
        logging.warning('entity from past')
        self.active = False

    return super(BasePassphrase, self).put(*args, **kwargs)

  @classmethod
  @db.transactional()
  def _UpdateMutableProperties(cls, key, changes):
    entity = cls.get(key)
    if not entity.active:
      raise cls.ACCESS_ERR_CLS('entity is inactive: %s.' % entity.target_id)

    for property_name, value in changes.iteritems():
      if property_name == 'hostname':
        value = cls.NormalizeHostname(value)
      setattr(entity, property_name, value)
    return super(BasePassphrase, entity).put()

  def UpdateMutableProperty(self, property_name, value):
    if not self.has_key():
      raise self.ACCESS_ERR_CLS('Volume should be in the db.')

    if property_name not in self.MUTABLE_PROPERTIES:
      raise ValueError

    self._UpdateMutableProperties(self.key(), {property_name: value})
    setattr(self, property_name, value)

  @property
  def target_id(self):
    return getattr(self, self.TARGET_PROPERTY_NAME)

  @target_id.setter
  def _set_target_id(self, value):
    return setattr(self, self.TARGET_PROPERTY_NAME, value)

  @property
  def secret(self):
    return getattr(self, self.SECRET_PROPERTY_NAME)

  @property
  def checksum(self):
    return hashlib.md5(self.secret).hexdigest()

  @classmethod
  def NormalizeHostname(cls, hostname, strip_fqdn=False):
    """Sanitizes a hostname for consistent search functionality.

    Args:
      hostname: str hostname to sanitize.
      strip_fqdn: boolean, if True removes fully qualified portion of hostname.
    Returns:
      str hostname.
    """
    #  call this during escrow create, to sanitize before storage.
    if strip_fqdn:
      hostname = hostname.partition('.')[0]
    return hostname.lower()


class User(db.Model):
  """User of the CauliflowerVest application."""

  _PERMISSION_PROPERTIES = {
      permissions.TYPE_BITLOCKER: 'bitlocker_perms',
      permissions.TYPE_DUPLICITY: 'duplicity_perms',
      permissions.TYPE_FILEVAULT: 'filevault_perms',
      permissions.TYPE_LUKS: 'luks_perms',
      permissions.TYPE_PROVISIONING: 'provisioning_perms',
      permissions.TYPE_APPLE_FIRMWARE: 'apple_firmware_perms',
      permissions.TYPE_LINUX_FIRMWARE: 'linux_firmware_perms',
      permissions.TYPE_WINDOWS_FIRMWARE: 'windows_firmware_perms',
  }

  # key_name = user's email address.
  user = db.UserProperty()
  # Select BitLocker operational permissions from ALL_PERMISSIONS.
  bitlocker_perms = db.StringListProperty()
  # Select Duplicity operational permissions from ALL_PERMISSIONS.
  duplicity_perms = db.StringListProperty()
  # Select FileVault operational permissions from ALL_PERMISSIONS.
  filevault_perms = db.StringListProperty()
  # Select Luks operational permissions from ALL_PERMISSIONS.
  luks_perms = db.StringListProperty()
  # Select Provisioning operational permissions from ALL_PERMISSIONS.
  provisioning_perms = db.StringListProperty()
  # Select Firmware operational permissions from ALL_PERMISSIONS.
  apple_firmware_perms = db.StringListProperty()
  linux_firmware_perms = db.StringListProperty()
  windows_firmware_perms = db.StringListProperty()

  @property
  def email(self):
    return self.user.email()

  def HasPerm(self, perm, permission_type):
    """Verifies the User has permissions.

    Args:
      perm: str, permission to verify, one of PERM_* class variables.
      permission_type: str, one of permissions.TYPE_* variables.
    Returns:
      Boolean. True if the user has the requested permission, False otherwise.
    Raises:
      ValueError: the requested permission_type was invalid or unknown.
    """
    perm_prop = self._PERMISSION_PROPERTIES.get(permission_type)
    if not perm_prop:
      raise ValueError('unknown permission_type: %s' % permission_type)

    base_perms = settings.DEFAULT_PERMISSIONS.get(permission_type, ())
    return perm in base_perms or perm in getattr(self, perm_prop, [])

  def SetPerms(self, perms, permission_type):
    """Sets the permissions to the User object.

    Args:
      perms: list of str, permissions from permissions.*.
      permission_type: str, one of permissions.TYPE_* variables.
    Raises:
      ValueError: the requested permission_type was invalid or unknown.
    """
    perm_prop = self._PERMISSION_PROPERTIES.get(permission_type)
    if not perm_prop:
      raise ValueError('unknown permission_type: %s' % permission_type)
    setattr(self, perm_prop, list(perms))


class AccessLog(db.Model):
  """Model for logging access to passphrases."""
  ip_address = db.StringProperty()
  message = db.StringProperty()
  mtime = db.DateTimeProperty(auto_now_add=True)
  query = db.StringProperty()
  successful = db.BooleanProperty(default=True)
  user = AutoUpdatingUserProperty()

  # Guaranteed unique, for pagination.
  paginate_mtime = db.StringProperty()

  def put(self):  # pylint: disable=g-bad-name
    """Override put to automatically calculate pagination properties."""
    counter = memcache.incr('AccessLogCounter', initial_value=0)
    self.paginate_mtime = '%s_%s' % (self.mtime, counter)
    super(AccessLog, self).put()

  @classmethod
  def Log(cls, request=None, **kwargs):
    """Puts a new AccessLog entity into Datastore.

    Args:
       request: a webapp Request object to fetch obtain details from.
       **kwargs: any key/value pair with a key corresponding to an existing
          AccessLog property name.
    """
    log = cls()
    for p in log.properties():
      if p in kwargs:
        setattr(log, p, kwargs[p])
    if request:
      log.query = '%s?%s' % (request.path, request.query_string)
      log.ip_address = request.remote_addr
    log.put()
