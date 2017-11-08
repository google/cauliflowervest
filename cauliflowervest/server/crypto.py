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

"""CauliflowerVest utility module."""

import json
import logging



from keyczar import keyczar
from keyczar import keyinfo
from keyczar import readers

from cauliflowervest.server import settings


# To add support for different internal encryption keys in the future, the
# below maps encryption key "types" to functions that fetch the key for you.
#
#
# These functions should return a list of dictionaries as documented below:
# [
#   {'versionNumber': int, version number of this key.
#    'aesKeyString': str, base64.urlsafe_b64encode encoded AES key.
#    'aesKeySize': int, optional, size in bits of the AES key. default of 128.
#    'hmacKeyString': str, base64.urlsafe_b64encode encoded HMAC key.
#    'hmacKeySize': int, optional, size in bits of the HMAC key. default of 256.
#    'status': str, Keyczar status like PRIMARY, ACTIVE, INACTIVE.
#   },
#   { ... },
# ]
#
# For more details, see Keyczar documentation: https://github.com/google/keyczar
#
ENCRYPTION_KEY_TYPES = {
    # REPLACE THIS WITH YOUR OWN SERVICE KEY RETRIEVAL METHOD.
    settings.KEY_TYPE_DATASTORE_FILEVAULT: lambda: settings.DEMO_KEYS,
    settings.KEY_TYPE_DATASTORE_XSRF: lambda: settings.DEMO_XSRF_SECRET,
    }


class Error(Exception):
  """Class for domain-specific exceptions."""


class CauliflowerVestReader(readers.Reader):
  """Keyczar Reader object for CauliflowerVest encryption."""

  def __init__(self):
    # Dict of all keys, with versionNumber as the dict key. Filled by LoadKeys.
    self.keys = {}
    # List of all key version dicts. Filled by LoadKeys.
    self.key_versions = []

  def LoadKeys(self, key_type):
    """Loads keys of a predefined encryption key type into the instance.

    Args:
      key_type: str, predefined type of encryption key to use.

    Raises:
      ValueError: When key cannot be found for the requested type.
      Error: There was an error obtaining the keys.
    """
    try:
      func = ENCRYPTION_KEY_TYPES[key_type]
    except KeyError:
      raise ValueError('Unknown key_type: %s' % key_type)

    keys = func()

    if not keys:
      raise ValueError('No keys returned for key_type: %s' % key_type)

    for key in keys:
      version_number = key['versionNumber']
      key['aesKeySize'] = key.get('aesKeySize', keyinfo.AES.default_size)
      key['hmacKeySize'] = key.get(
          'hmacKeySize', keyinfo.HMAC_SHA1.default_size)
      if version_number in self.keys:
        logging.error(
            'LoadKeys() duplicate key versionNumbers: %s', version_number)
        logging.warning('first key: %s', self.keys[version_number])
        logging.warning('dupe key: %s', key)
      self.keys[version_number] = key

      self.key_versions.append({
          'versionNumber': version_number,
          'status': key['status'],
          'exportable': False,
      })

  def GetMetadata(self):
    """Return the KeyMetadata for the key set being read.

    Returns:
      str, JSON representation of KeyMetadata object

    Raises:
      ValueError: When no keys are loaded.
    """
    if not self.keys or not self.key_versions:
      raise ValueError('GetMetadata() called before LoadKeys()')

    data = {
        'name': 'filevault_keys',
        'purpose': keyinfo.DECRYPT_AND_ENCRYPT.name,
        'type': keyinfo.AES.name,
        'encrypted': False,
        'versions': self.key_versions,
    }
    return json.dumps(data)

  def GetKey(self, version_number):
    """Return the key corresponding to the given version.

    Args:
      version_number: int, unused version number for the desired key.

    Returns:
      str, JSON representation of a Key object

    Raises:
      ValueError: When no keys are loaded, or the version requested isn't found.
    """
    if not self.keys or not self.key_versions:
      raise ValueError('GetKey() called before LoadKeys()')

    key = self.keys.get(version_number, None)
    if not key:
      raise ValueError('GetKey() unknown version_number: %d', version_number)
    data = {
        'mode': keyinfo.CBC.name,
        'size': key['aesKeySize'],
        'aesKeyString': key['aesKeyString'],
        'hmacKey': {
            'size': key['hmacKeySize'],
            'hmacKeyString': key['hmacKeyString'],
        },
    }
    return json.dumps(data)

  def Close(self):
    return


def AreEncryptionKeysAvailable(key_type=settings.KEY_TYPE_DEFAULT_FILEVAULT):
  """Returns True if the encryption keys are available."""
  reader = CauliflowerVestReader()
  try:
    reader.LoadKeys(key_type)
  except (Error, ValueError):
    logging.exception('Could not load encryption keys.')
    return False
  return True


def Decrypt(encrypted_data, key_name=None, key_type=None):  # pylint: disable=unused-argument
  """Decrypts and returns encrypted_data.

  Args:
    encrypted_data: blob, data to decrypt.
    key_name: str, key_name for encryption to use.
    key_type: str, predefined type of encryption to use.
  Returns:
    decrypted blob data.
  """
  if not key_type:
    key_type = settings.KEY_TYPE_DEFAULT_FILEVAULT
  if not encrypted_data:
    return encrypted_data

  reader = CauliflowerVestReader()
  reader.LoadKeys(key_type)
  crypter = keyczar.Crypter(reader=reader)
  return crypter.Decrypt(encrypted_data)


def Encrypt(data, key_name=None, key_type=None):  # pylint: disable=unused-argument
  """Encrypts data and returns.

  Args:
    data: blob, data to encrypt.
    key_name: str, key_name for encryption to use.
    key_type: str, predefined type of encryption to use.
  Returns:
    encrypted blob data.
  """
  if not key_type:
    key_type = settings.KEY_TYPE_DEFAULT_FILEVAULT
  if not data:
    return data

  reader = CauliflowerVestReader()
  reader.LoadKeys(key_type)
  crypter = keyczar.Crypter(reader=reader)
  return crypter.Encrypt(data)
