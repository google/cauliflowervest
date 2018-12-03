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

"""Transperent encryption of properties in db."""
import base64
import json

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util import Counter

from google.appengine.ext import db

from cauliflowervest.server import crypto
from cauliflowervest.server import settings
from common import cloud_kms


class _EnvelopeCloudKms(object):
  """Envelope encryption with Cloud KMS."""
  _KEYRING_NAME = 'keyring2'

  @classmethod
  def _EncryptMsg(cls, key, plaintext):
    ctr = Counter.new(AES.block_size * 8)
    # needed for compatibility with old format.
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    return base64.urlsafe_b64encode(iv + cipher.encrypt(plaintext))

  @classmethod
  def _DecryptMsg(cls, key, data):
    data = base64.urlsafe_b64decode(str(data))

    ctr = Counter.new(AES.block_size * 8)
    ciphertext = data[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    return cipher.decrypt(ciphertext)

  @classmethod
  def Encrypt(cls, plaintext, key_name):
    """Encrypts data and returns."""
    data_encryption_key = Random.new().read(32)  # 32 bytes, 256 bits key
    encrypted_key = cloud_kms.Encrypt(
        data_encryption_key, key_name, cls._KEYRING_NAME)
    ciphertext = cls._EncryptMsg(data_encryption_key, plaintext)

    # base64 encoded key should not exceed 3x original key size.
    assert len(encrypted_key) < 10000

    return '%04d%s%s' % (len(encrypted_key), encrypted_key, ciphertext)

  @classmethod
  def Decrypt(cls, blob, key_name):
    length = int(blob[:4])
    key_and_ctx = blob[4:]
    encrypted_key = key_and_ctx[:length]
    ciphertext = key_and_ctx[length:]
    dek = cloud_kms.Decrypt(encrypted_key, key_name, cls._KEYRING_NAME)

    return cls._DecryptMsg(dek, ciphertext)


_CRYPTO_BACKEND = {
    'keyczar': crypto,
    'envelope_cloud_kms': _EnvelopeCloudKms,
}


class EncryptedBlobProperty(db.BlobProperty):
  """BlobProperty class that encrypts/decrypts data seamlessly on get/set."""

  _key_name = None

  def __init__(self, key_name, *args, **kwargs):
    super(EncryptedBlobProperty, self).__init__(*args, **kwargs)
    self._key_name = key_name

  def _Decrypt(self, value):
    # Attempt to load the contents as json (the new blob format) and, if that
    # fails, assume the result is encoded using KeyCzar's non-standard base64
    # format.
    try:
      description = json.loads(value)
      if not isinstance(description, dict):
        raise ValueError
    except ValueError:
      # old format, contains base64 data
      return crypto.Decrypt(value)
    else:
      backend = description.get('backend')
      assert backend and backend in _CRYPTO_BACKEND

      return _CRYPTO_BACKEND[backend].Decrypt(
          description['value'], key_name=self._key_name)

  def _Encrypt(self, value):
    encrypted = _CRYPTO_BACKEND[settings.DEFAULT_CRYPTO_BACKEND].Encrypt(
        value, key_name=self._key_name)
    return json.dumps({
        'backend': settings.DEFAULT_CRYPTO_BACKEND,
        'value': encrypted,
    })

  # pylint: disable=g-bad-name
  def make_value_from_datastore(self, value):
    """Decrypts the blob value coming from Datastore."""
    return super(EncryptedBlobProperty, self).make_value_from_datastore(
        db.Blob(str(self._Decrypt(value))))

  # pylint: disable=g-bad-name
  def get_value_for_datastore(self, model_instance):
    """Encrypts the blob value on it's way to Datastore."""
    raw_blob = super(
        EncryptedBlobProperty, self).get_value_for_datastore(model_instance)
    return db.Blob(str(self._Encrypt(raw_blob)))
