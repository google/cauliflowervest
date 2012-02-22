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

"""Configurable settings module for the server."""




import base64
import os

from cauliflowervest.server import permissions

DEVELOPMENT = 'Development' in os.environ.get('SERVER_SOFTWARE', '')




# If set to False, models.User is checked for ESCROW permission instead.
ALLOW_ALL_DOMAIN_USERS_TO_ESCROW = False

# If ALLOW_ALL_DOMAIN_USERS_TO_ESCROW = True, user accounts attempting to
# esrow must be in the form <username>@AUTH_DOMAIN or escrow will be denied.
AUTH_DOMAIN = 'example.com'

DEFAULT_EMAIL_DOMAIN = 'example.com'
DEFAULT_EMAIL_SENDER = ''
DEFAULT_EMAIL_REPLY_TO = ''

FILEVAULT_PERMISSIONS_KEY = 'filevault_perms'

GROUPS = {
    FILEVAULT_PERMISSIONS_KEY: [
        ('front-line-support', (permissions.RETRIEVE,)),
        ('developers', (permissions.SET_REGULAR,)),
        ('security-team', (permissions.SET_SILENT,)),
        ]
    }

KEY_TYPE_DATASTORE_FILEVAULT = 'key_type_datastore_filevault'
KEY_TYPE_DEFAULT = KEY_TYPE_DATASTORE_FILEVAULT
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

# These email addresses will be notified when a user of the named permission
# fetches a passphrase, in addition to the default behavior.
RETRIEVE_AUDIT_ADDRESSES = []
SILENT_AUDIT_ADDRESSES = []

HELPDESK_NAME = 'helpdesk'
RETRIEVAL_EMAIL_SUBJECT = 'FileVault Passphrase retrieval notification.'
RETRIEVAL_EMAIL_BODY = """
The FileVault encryption passphrase for your Mac has been recovered. This
passphrase allows for access to your encrypted hard disk, which may pose a
security risk.

Retrieved By: %(retrieved_by)s
Hostname: %(hostname)s
Platform UUID: %(platform_uuid)s
Serial Number: %(serial)s
HDD Serial: %(hdd_serial)s
Volume UUID: %(volume_uuid)s

If you are unaware of this event and this Mac is not in the hands of
%(helpdesk_name)s, please respond to this message immediately.
"""

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')