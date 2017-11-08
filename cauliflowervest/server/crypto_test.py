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

"""crypto module tests."""

import json



import mock

from absl.testing import absltest
from cauliflowervest.server import crypto


class CauliflowerVestReaderTest(absltest.TestCase):
  """Test the crypto.CauliflowerVestReader class."""

  def setUp(self):
    super(CauliflowerVestReaderTest, self).setUp()
    self.r = crypto.CauliflowerVestReader()

  def _LoadTestKeys(self):
    """Helper function that loads test keys into the CauliflowerVestReader instance."""
    self.test_keys = [
        {'versionNumber': 1,
         'aesKeyString': 'aeskey1',
         'aesKeySize': 192,
         'hmacKeyString': 'hmackey1',
         'hmacKeySize': 256,
         'status': 'PRIMARY',
        },
        {'versionNumber': 2,
         'aesKeyString': 'aeskey2',
         'hmacKeyString': 'hmackey2',
         'status': 'ACTIVE',
        },
        ]
    key_type = 'test-type'
    crypto.ENCRYPTION_KEY_TYPES[key_type] = lambda: self.test_keys
    self.r.LoadKeys(key_type)

  def testLoadKeysUnknownType(self):
    self.assertRaises(ValueError, self.r.LoadKeys, 'unknown-type-for-sure')


  def testLoadKeysNoKeys(self):
    key_type = 'test-type'
    crypto.ENCRYPTION_KEY_TYPES[key_type] = lambda: []
    self.assertRaises(ValueError, self.r.LoadKeys, key_type)

  def testLoadKeys(self):
    self._LoadTestKeys()

    # Verify keys dict and key_versions list are the expected size.
    self.assertEqual(2, len(self.r.keys))
    self.assertEqual(2, len(self.r.key_versions))

    # Verify key #1 was loaded correctly into keys dict.
    self.assertEqual(1, self.r.keys[1]['versionNumber'])
    self.assertEqual('aeskey1', self.r.keys[1]['aesKeyString'])
    self.assertEqual(192, self.r.keys[1]['aesKeySize'])
    self.assertEqual('hmackey1', self.r.keys[1]['hmacKeyString'])
    self.assertEqual(256, self.r.keys[1]['hmacKeySize'])
    self.assertEqual('PRIMARY', self.r.keys[1]['status'])

    # Verify that key #2 was loaded correctly into keys dict.
    self.assertEqual(2, self.r.keys[2]['versionNumber'])
    self.assertEqual('aeskey2', self.r.keys[2]['aesKeyString'])
    self.assertEqual(
        crypto.keyinfo.AES.default_size, self.r.keys[2]['aesKeySize'])
    self.assertEqual('hmackey2', self.r.keys[2]['hmacKeyString'])
    self.assertEqual(
        crypto.keyinfo.HMAC_SHA1.default_size, self.r.keys[2]['hmacKeySize'])
    self.assertEqual('ACTIVE', self.r.keys[2]['status'])

    # Verify keys was loaded correctly into keys dict.
    self.assertEqual(1, self.r.key_versions[0]['versionNumber'])
    self.assertEqual('PRIMARY', self.r.key_versions[0]['status'])
    self.assertFalse(self.r.key_versions[0]['exportable'])
    self.assertEqual(2, self.r.key_versions[1]['versionNumber'])
    self.assertEqual('ACTIVE', self.r.key_versions[1]['status'])
    self.assertFalse(self.r.key_versions[1]['exportable'])

  def testGetMetadataBeforeLoadKeys(self):
    self.assertRaises(ValueError, self.r.GetMetadata)

  def testGetMetadata(self):
    self._LoadTestKeys()
    json_output_str = self.r.GetMetadata()
    d = json.loads(json_output_str)

    self.assertEqual('filevault_keys', d['name'])
    self.assertEqual(crypto.keyinfo.DECRYPT_AND_ENCRYPT.name, d['purpose'])
    self.assertEqual(crypto.keyinfo.AES.name, d['type'])
    self.assertEqual(self.r.key_versions, d['versions'])
    self.assertFalse(d['encrypted'])

  def testGetKeyBeforeLoadKeys(self):
    self.assertRaises(ValueError, self.r.GetKey, 123)

  def testGetKeyUnknownVersion(self):
    self.assertRaises(ValueError, self.r.GetKey, 'this-key-does-not-exist')

  def testGetKey(self):
    self._LoadTestKeys()
    json_output_str = self.r.GetKey(1)
    d = json.loads(json_output_str)

    self.assertEqual(crypto.keyinfo.CBC.name, d['mode'])
    self.assertEqual(self.test_keys[0]['aesKeySize'], d['size'])
    self.assertEqual(self.test_keys[0]['aesKeyString'], d['aesKeyString'])
    self.assertEqual(self.test_keys[0]['hmacKeySize'], d['hmacKey']['size'])
    self.assertEqual(
        self.test_keys[0]['hmacKeyString'], d['hmacKey']['hmacKeyString'])

  def testGetKeyWithKey2(self):
    self._LoadTestKeys()
    json_output_str = self.r.GetKey(2)
    d = json.loads(json_output_str)

    self.assertEqual(crypto.keyinfo.CBC.name, d['mode'])
    self.assertEqual(self.test_keys[1]['aesKeySize'], d['size'])
    self.assertEqual(self.test_keys[1]['aesKeyString'], d['aesKeyString'])
    self.assertEqual(self.test_keys[1]['hmacKeySize'], d['hmacKey']['size'])
    self.assertEqual(
        self.test_keys[1]['hmacKeyString'], d['hmacKey']['hmacKeyString'])


class CryptoModuleTest(absltest.TestCase):
  """Test the crypto module."""

  @mock.patch.object(crypto, 'CauliflowerVestReader')
  @mock.patch.object(crypto.keyczar, 'Crypter')
  def testDecrypt(self, crypter, cauliflowervest_reader):
    encrypted_data = 'foodata'
    key_type = 'footype'

    mock_reader = mock.MagicMock()
    cauliflowervest_reader.return_value = mock_reader

    mock_crypter = mock.MagicMock()
    mock_crypter.Decrypt.return_value = 'result'
    crypter.return_value = mock_crypter

    r = crypto.Decrypt(encrypted_data, key_type=key_type)
    self.assertEqual(r, 'result')

    mock_reader.LoadKeys.assert_called_once_with(key_type)
    crypter.assert_called_once_with(reader=mock_reader)
    mock_crypter.Decrypt.assert_called_once_with(encrypted_data)

  @mock.patch.object(crypto, 'CauliflowerVestReader')
  @mock.patch.object(crypto.keyczar, 'Crypter')
  def testEncrypt(self, crypter, cauliflowervest_reader):
    data = 'foodata'
    key_type = 'footype'

    mock_reader = mock.MagicMock()
    cauliflowervest_reader.return_value = mock_reader

    mock_crypter = mock.MagicMock()
    mock_crypter.Encrypt.return_value = 'result'
    crypter.return_value = mock_crypter

    r = crypto.Encrypt(data, key_type=key_type)
    self.assertEqual(r, 'result')

    mock_reader.LoadKeys.assert_called_once_with(key_type)
    crypter.assert_called_once_with(reader=mock_reader)
    mock_crypter.Encrypt.assert_called_once_with(data)

  @mock.patch.object(crypto, 'CauliflowerVestReader')
  def testAreEncryptionKeysAvailableWhenAvailable(self, cauliflowervest_reader):
    t = 'footype'
    mock_reader = mock.MagicMock()
    cauliflowervest_reader.return_value = mock_reader

    self.assertTrue(crypto.AreEncryptionKeysAvailable(key_type=t))

    mock_reader.LoadKeys.assert_called_once_with(t)

  @mock.patch.object(crypto, 'CauliflowerVestReader')
  def testAreEncryptionKeysAvailableWithLoadKeysError(self, cauliflowervest_reader):
    t = 'footype'
    mock_reader = mock.MagicMock()
    cauliflowervest_reader.return_value = mock_reader
    mock_reader.LoadKeys.side_effect = crypto.Error()

    self.assertFalse(crypto.AreEncryptionKeysAvailable(key_type=t))
    mock_reader.LoadKeys.assert_called_once_with(t)


if __name__ == '__main__':
  absltest.main()
