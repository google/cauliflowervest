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

"""App Engine Models for CauliflowerVest web application."""



import logging

from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db

from cauliflowervest import settings as base_settings
from cauliflowervest.server import crypto
from cauliflowervest.server import permissions


class Error(Exception):
  """Class for domain specific exceptions."""


class FileVaultAccessError(Error):
  """There was an error accessing a FileVault passphrase."""
  request = None
  error_code = 400

  def __init__(self, message, request=None):
    super(FileVaultAccessError, self).__init__(message)
    self.request = request


class FileVaultAccessDeniedError(FileVaultAccessError):
  """Accessing a passphrase was denied."""
  error_code = 403


class FileVaultMissingError(FileVaultAccessError):
  """A desired passphrase is missing."""
  error_code = 404


# Here so that AutoUpdatingUserProperty will work without dependency cycles.
def GetCurrentUser(get_model_user=False):
  """Returns a users.User object for the current logged in user.

  If the current logged in user is an App Engine admin, a User entity will
  be created for them with permissions.SET_REGULAR permissions.

  Args:
    get_model_user: boolean, default False, True to return a models.User obj.
  Returns:
    users.User object, or models.User object if get_model_user is True.
  """
  user = users.get_current_user()
  if user:
    if get_model_user:
      user_entity = User.get_by_key_name(user.email())
      if not user_entity and users.is_current_user_admin():
        # Automatically create User entities with full permissions for
        # users with admin privileges.
        user_entity = User(key_name=user.email())
        user_entity.filevault_perms = list(permissions.SET_REGULAR)
        user_entity.user = users.User(user.email())
        user_entity.put()
      user = user_entity
  return user


class EncryptedBlobProperty(db.BlobProperty):
  """BlobProperty class that encrypts/decrypts data seamlessly on get/set."""

  # pylint: disable-msg=C6409
  def make_value_from_datastore(self, value):
    """Decrypts the blob value coming from Datastore."""
    return super(EncryptedBlobProperty, self).make_value_from_datastore(
        crypto.Decrypt(value))

  # pylint: disable-msg=C6409
  def get_value_for_datastore(self, model_instance):
    """Encrypts the blob value on it's way to Datastore."""
    raw_blob = super(
        EncryptedBlobProperty, self).get_value_for_datastore(model_instance)
    return db.Blob(crypto.Encrypt(raw_blob))


class AutoUpdatingUserProperty(db.UserProperty):
  """UserProperty that sets the current users.User if not already set."""

  # pylint: disable-msg=C6409
  def get_value_for_datastore(self, model_instance):
    """If the value is not set, set it to the current user."""
    user = super(AutoUpdatingUserProperty, self).get_value_for_datastore(
        model_instance)
    return user or GetCurrentUser()


class FileVaultVolume(db.Model):
  """Model for storing FileVault Volume passphrases, with various metadata."""

  # Properties that are required to be set when putting a new FileVaultVolume.
  REQUIRED_PROPERTIES = base_settings.FILEVAULT_REQUIRED_PROPERTIES + [
      'passphrase', 'volume_uuid']

  SEARCH_FIELDS = [
      ('created_by', 'Escrow Username'),
      ('hdd_serial', 'Hard Drive Serial Number'),
      ('hostname', 'Hostname'),
      ('serial', 'Mac Serial Number'),
      ('owner', 'Owner Username'),
      ('platform_uuid', 'Platform UUID'),
      ('volume_uuid', 'Volume UUID'),
      ]

  passphrase = EncryptedBlobProperty()  # passphrase to unlock encrypted volume.
  volume_uuid = db.StringProperty()  # Volume UUID of the encrypted volume.
  active = db.BooleanProperty(default=True)  # is this key active or not?
  platform_uuid = db.StringProperty()  # sp_platform_uuid in facter.
  owner = db.StringProperty()  # user owning the Mac.
  hostname = db.StringProperty()  # name of the Mac.
  serial = db.StringProperty()  # serial number of the Mac.
  hdd_serial = db.StringProperty()  # hard drive disk serial number.
  created = db.DateTimeProperty(auto_now_add=True)
  # NOTE(user): created_by is the user that created the object.
  #   For self-service encryption, owner/created_by may the same.
  #   Furthermore, created_by may go away once we have unattended encryption
  #   via machine/certificate-based auth.
  created_by = AutoUpdatingUserProperty()

  # pylint: disable-msg=C6409
  def put(self, *args, **kwargs):
    """Disallow updating an existing entity, and enforce key_name.

    Returns:
      The key of the instance (either the existing key or a new key).
    Raises:
      FileVaultAccessError: an existing entity was attempted to be put, or a
          required property was empty or not set.
    """
    if not self.has_key():
      raise FileVaultAccessError('Cannot put a FileVaultVolume without a key.')
    if FileVaultVolume.get_by_key_name(self.key().name()):
      raise FileVaultAccessError('Cannot update an existing FileVaultVolume.')
    for prop_name in self.REQUIRED_PROPERTIES:
      if not getattr(self, prop_name, None):
        raise FileVaultAccessError('Required property empty: %s' % prop_name)
    return super(FileVaultVolume, self).put(*args, **kwargs)


class User(db.Model):
  """User of the CauliflowerVest application."""

  # key_name = user's email address.

  user = db.UserProperty()
  # Select FileVault operational permissions from ALL_PERMISSIONS.
  filevault_perms = db.StringListProperty()

  def HasPerm(self, perm, perm_prop='filevault_perms'):
    """Verifies the the User has permissions.

    Args:
      perm: str, permission to verify, one of PERM_* class variables.
      perm_prop: str, property name of permissions to check; defaults to
          filevault_perms.
    Returns:
      Boolean. True if the user has the requested permission, False otherwise.
    Raises:
      ValueError: the requested permission is unknown.
    """
    return perm in getattr(self, perm_prop, [])


class FileVaultAccessLog(db.Model):
  """Model for logging access to FileVault passphrases."""
  ip_address = db.StringProperty()
  message = db.StringProperty()
  mtime = db.DateTimeProperty(auto_now_add=True)
  query = db.StringProperty()
  successful = db.BooleanProperty(default=True)
  user = AutoUpdatingUserProperty()

  # Guaranteed unique, for pagination.
  paginate_mtime = db.StringProperty()

  def put(self):  # pylint: disable-msg=C6409
    """Override put to automatically calculate pagination properties."""
    counter = memcache.incr('FileVaultAccessLogCounter', initial_value=0)
    self.paginate_mtime = '%s_%s' % (self.mtime, counter)
    super(FileVaultAccessLog, self).put()

  @classmethod
  def Log(cls, request=None, **kwargs):
    """Puts a new FileVaultAccessLog entity into Datastore.

    Args:
      request: a webapp Request object to fetch obtain details from.
      **kwargs: any key/value pair with a key corresponding to an existing
          FileVaultAccessLog property name.
    """
    log = FileVaultAccessLog()
    for p in log.properties():
      if p in kwargs:
        setattr(log, p, kwargs[p])
    if request:
      log.query = '%s?%s' % (request.path, request.query_string)
      log.ip_address = request.remote_addr
    log.put()