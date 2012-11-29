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

"""CauliflowerVest client main entry module."""



import base64
import os

from cauliflowervest.client import util

KEYCHAIN_PATH = '/Library/Keychains/FileVaultMaster.keychain'


def Create(open_=open):
  """Create a keychain that FileVault will use for disk encryption.

  Args:
    open_: Callable, dependency injection for "open" builtin.

  Returns:
    Tuple of blobs, (pub_only_keychain, full_keychain, passphrase).

  Raises:
    AssertionError: For all exception cases.
  """
  # Input to send to create a compliant keychain.
  script = '\n'.join((
      'FileVault Recovery Key', 'r', '1024', 'y', 'b', 's', 'y',
      'FileVault Recovery Key', '', '', '', '', '', 'y', ''))
  # 160 cryptographically random bits, encoded with 32 printable characters.
  passphrase = base64.b32encode(os.urandom(20))

  # Create the full keychain (pub + priv), and (pub) cert file.
  returncode, unused_stdout, unused_stderr = util.Exec((
      '/usr/bin/certtool', 'c', 'c', 'k=' + KEYCHAIN_PATH,
      'o=%s.pem' % KEYCHAIN_PATH, 'a', 'p=' + passphrase), script)
  assert returncode == 0, 'Could not create full keychain (%s).' % returncode

  # Get that data, and remove the keychain, to ...
  full_keychain = open_(KEYCHAIN_PATH, 'r').read()
  Remove()
  # ... replace it with the public-key-only version.
  returncode, unused_stdout, unused_stderr = util.Exec((
      '/usr/bin/security', 'create-keychain', '-p', passphrase, KEYCHAIN_PATH))
  assert returncode == 0, 'Could not create pub keychain (%s).' % returncode
  returncode, unused_stdout, unused_stderr = util.Exec((
      '/usr/bin/certtool', 'i', KEYCHAIN_PATH + '.pem', 'k=' + KEYCHAIN_PATH))
  assert returncode == 0, 'Could not import pub keychain (%s).' % returncode
  pub_only_keychain = open_(KEYCHAIN_PATH, 'r').read()

  return pub_only_keychain, full_keychain, passphrase


def Remove():
  """Ensure that no pre-existing keychain is used, by removing it.

  Raises:
    AssertionError: For all exception cases.
  """
  # TODO(user): Ensure that this "securely" deletes the sensitive data.
  returncode, unused_stdout, unused_stderr = util.Exec(
      ('/usr/bin/security', 'delete-keychain', KEYCHAIN_PATH))
  # Error code 50 is file did not exist.
  assert returncode in (0, 50), (
      'Could not remove old keychain (%s).' % returncode)