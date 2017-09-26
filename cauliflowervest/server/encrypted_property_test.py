#
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
#
#
import base64



import mock

from absl.testing import absltest
from cauliflowervest.server import encrypted_property


class EncryptedPropertyModelTest(absltest.TestCase):

  @mock.patch.object(encrypted_property.cloud_kms, 'Encrypt')
  @mock.patch.object(encrypted_property.cloud_kms, 'Decrypt')
  def testEnvelopeEncryption(self, decrypt_mock, encrypt_mock):
    # Result is larger then original key.
    # prevent using enncrypted key without "decrypt".
    encrypt_mock.side_effect = lambda x, a1, a2: base64.b64encode(x)
    decrypt_mock.side_effect = lambda x, a1, a2: base64.b64decode(x)

    envelope = encrypted_property._EnvelopeCloudKms()

    data = '1234-56789-ABVC'

    self.assertEqual(data, envelope.Decrypt(envelope.Encrypt(data, '1'), '1'))


if __name__ == '__main__':
  absltest.main()
