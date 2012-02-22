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

"""CauliflowerVest glue code module."""



import logging
import os
import urlparse

from cauliflowervest.client import client
from cauliflowervest.client import corestorage
from cauliflowervest.client import util


ENCRYPTION_SUCCESS_MESSAGE = (
    'Encryption enabled and passphrase escrowed successfully.\n\n'
    'Please restart the computer to start encryption!')
ENCRYPTION_FAILED_MESSAGE = (
    'Encryption was not enabled. Please try again.')
ESCROW_FAILED_MESSAGE = (
    'Encryption was enabled, but escrowing the recovery passphrase failed.\n\n'
    'Please reboot, manually disable FileVault in '
    'System Preferences -> Security & Privacy, '
    'wait for decryption to complete, reboot again, and run CauliflowerVest again.\n')

CSFDE_RETURN_AUTH_FAIL = 99
CSFDE_PATH = '/usr/local/bin/csfde'


class Error(Exception):
  """Base error."""


class InputError(Error):
  """Base class for all errors raised for invalid user input."""


class OptionError(Error):
  """Base class for all errors raised by options."""


def ApplyEncryption(fvclient, username, password):
  """Turn encryption on."""

  # Supply entropy to the system before csfde uses /dev/random.
  try:
    entropy = util.RetrieveEntropy()
    util.SupplyEntropy(entropy)
  except util.EntropyError, e:
    raise Error('Entropy operations failed: %s' % str(e))

  root_disk = util.GetRootDisk()
  try:
    csfde_plist = util.GetPlistFromExec((
        CSFDE_PATH, root_disk, username, '-'), stdin=password)
  except util.ExecError, e:
    if e.returncode == CSFDE_RETURN_AUTH_FAIL:
      raise InputError(
          'Authentication problem with local account.  Drive NOT encrypted.')
    elif e.returncode != 0:
      logging.error('csfde failed with stderr:\n%s', e.stderr)
      raise Error('Problem running csfde (exit status = %d)' % e.returncode)
    else:
      logging.exception('Problem running csfde.')
      raise Error('Problem running csfde', e)
  fvclient.SetOwner(username)

  return GetEncryptionResults(csfde_plist)


def CheckEncryptionPreconditions():
  # As far as our current understanding, we can't apply encryption if no
  # recovery partition is on the disk. If we attempt to do so csfde fails
  # inside Apple's code when it calls -[DADisk description] on a null pointer,
  # presumably the recovery partition it expected to find.
  if not corestorage.GetRecoveryPartition():
    raise OptionError('Recovery partition must exist.')
  # We can't apply encryption if core storage is already in place.
  if corestorage.GetState() != corestorage.State.none:
    raise OptionError(
        'Core storage must be disabled. If you just reverted, please reboot.')
  # We can't get a recovery passphrase if a keychain is in place.
  if os.path.exists('/Library/Keychains/FileVaultMaster.keychain'):
    raise OptionError(
        'This tool cannot operate with a FileVaultMaster keychain in place.')


def GetEncryptionResults(csfde_plist):
  """Parse the (plist) output of csfde."""
  recovery_token = csfde_plist.get('recovery_password')
  if not recovery_token:
    raise Error('Could not get recovery token!')
  volume_uuid = csfde_plist.get('LVUUID')
  if not volume_uuid:
    raise Error('Could not get volume UUID!')
  return volume_uuid, recovery_token


def GetEscrowClient(server_url, credentials, login_type=None):
  try:
    hostname = urlparse.urlparse(server_url)[1]
    if login_type is None or login_type == 'clientlogin':
      opener = client.BuildClientLoginOpener(hostname, credentials)
    else:
      raise NotImplementedError()

    fvclient = client.FileVaultClient(server_url, opener)
    fvclient.GetAndValidateMetadata()
    return fvclient
  except client.Error, e:
    raise Error(e)