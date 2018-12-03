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

"""Configurable settings module for the server."""

import base64
import os
import sys

from cauliflowervest.server import permissions

DEBUG = False
DEVELOPMENT = ('Development' in os.environ.get('SERVER_SOFTWARE', '')
               and 'testbed' not in os.environ.get('SERVER_SOFTWARE', ''))
TEST = 'unittest2' in sys.modules or 'unittest' in sys.modules


DEFAULT_CRYPTO_BACKEND = 'keyczar'

DEFAULT_EMAIL_DOMAIN = 'example.com'
DEFAULT_EMAIL_SENDER = 'user@example.com'
DEFAULT_EMAIL_REPLY_TO = 'diff-user@example.com'

# These are the default permissions that are conferred to all domain users. This
# replaces the old ALLOW_ALL_DOMAIN_USERS_TO_ESCROW setting. To achieve the same
# effect, simply add or remove permissions.ESCROW to the set of default perms
# for the relevant key types below.
DEFAULT_PERMISSIONS = {
    permissions.TYPE_BITLOCKER: (permissions.ESCROW, permissions.RETRIEVE_OWN),
    permissions.TYPE_DUPLICITY: (permissions.ESCROW, permissions.RETRIEVE_OWN),
    permissions.TYPE_FILEVAULT: (permissions.ESCROW, permissions.RETRIEVE_OWN),
    permissions.TYPE_LUKS: (permissions.ESCROW, permissions.RETRIEVE_OWN),
    permissions.TYPE_PROVISIONING: (permissions.ESCROW,
                                    permissions.RETRIEVE_OWN,
                                    permissions.RETRIEVE_CREATED_BY),
    permissions.TYPE_APPLE_FIRMWARE: (permissions.ESCROW,
                                      permissions.RETRIEVE_OWN),
    permissions.TYPE_LINUX_FIRMWARE: (permissions.ESCROW,
                                      permissions.RETRIEVE_OWN),
    permissions.TYPE_WINDOWS_FIRMWARE: (permissions.ESCROW,
                                        permissions.RETRIEVE_OWN),
}

GROUPS = {
    permissions.TYPE_BITLOCKER: [
        ('front-line-support', (permissions.RETRIEVE,)),
        ('developers', (permissions.SET_REGULAR,)),
        ('security-team', (permissions.SET_SILENT_RETRIEVE_WITH_AUDIT_EMAIL,)),
        ],
    permissions.TYPE_FILEVAULT: [
        ('front-line-support', (permissions.RETRIEVE,
                                permissions.CHANGE_OWNER)),
        ('developers', (permissions.SET_REGULAR,)),
        ('security-team', (permissions.SET_SILENT_RETRIEVE_WITH_AUDIT_EMAIL,)),
        ],
    }


KEY_TYPE_DATASTORE_FILEVAULT = 'key_type_datastore_filevault'
KEY_TYPE_DEFAULT_FILEVAULT = KEY_TYPE_DATASTORE_FILEVAULT
KEY_TYPE_DATASTORE_XSRF = 'key_type_datastore_xsrf'
KEY_TYPE_DEFAULT_XSRF = KEY_TYPE_DATASTORE_XSRF

# Turn to False to support v0.8 clients.
XSRF_PROTECTION_ENABLED = True

# The DEMO_KEYS list is purely for example only.  See the CauliflowerVest
# Google Code documentation for more information on how to integrate enterprise
# key servers.
DEMO_KEYS = [
    {'versionNumber': 1,
     'aesKeyString': base64.urlsafe_b64encode('16_byte_string__'),
     'aesKeySize': 128,
     'hmacKeyString': base64.urlsafe_b64encode(
         '32_byte_string_bbbbbbbbbbbbbbbbb'),
     'hmacKeySize': 256,
     'status': 'PRIMARY',
    },
]
# This DEMO value should be kept secret and safe in a similar manner.
DEMO_XSRF_SECRET = os.environ.get('CURRENT_VERSION_ID', 'random_default_value')

# These email addresses will be notified when a user of the named permission
# fetches a passphrase, in addition to the default behavior.
RETRIEVE_AUDIT_ADDRESSES = []
SILENT_AUDIT_ADDRESSES = []

HELPDESK_NAME = 'helpdesk'
HELPDESK_EMAIL = 'helpdesk@example.com'

BITLOCKER_RETRIEVAL_EMAIL_SUBJECT = (
    'BitLocker Windows disk encryption recovery key retrieval notification')

DUPLICITY_RETRIEVAL_EMAIL_SUBJECT = (
    'Duplicity Linux backup encryption key pair retrieval notification')

FILEVAULT_RETRIEVAL_EMAIL_SUBJECT = (
    'FileVault 2 Mac disk encryption passphrase retrieval notification')

LUKS_RETRIEVAL_EMAIL_SUBJECT = (
    'Luks Linux disk encryption passphrase retrieval notification')

PROVISIONING_RETRIEVAL_EMAIL_SUBJECT = (
    'Provisioning password retrieval notification')

APPLE_FIRMWARE_RETRIEVAL_EMAIL_SUBJECT = (
    'Apple Firmware password retrieval notification')

LINUX_FIRMWARE_RETRIEVAL_EMAIL_SUBJECT = (
    'Linux Firmware password retrieval notification')

WINDOWS_FIRMWARE_RETRIEVAL_EMAIL_SUBJECT = (
    'Windows Firmware password retrieval notification')

if TEST:
  DEFAULT_EMAIL_DOMAIN = 'example.com'
