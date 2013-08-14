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

DEBUG = False
DEVELOPMENT = 'Development' in os.environ.get('SERVER_SOFTWARE', '')


DEFAULT_EMAIL_DOMAIN = 'example.com'
DEFAULT_EMAIL_SENDER = ''
DEFAULT_EMAIL_REPLY_TO = ''

# These are the default permissions that are conferred to all domain users. This
# replaces the old ALLOW_ALL_DOMAIN_USERS_TO_ESCROW setting. To achieve the same
# effect, simply add or remove permissions.ESCROW to the set of default perms
# for the relevant key types below.
DEFAULT_PERMISSIONS = {
    permissions.TYPE_BITLOCKER: (permissions.ESCROW,),
    permissions.TYPE_DUPLICITY: (permissions.ESCROW, permissions.RETRIEVE_OWN),
    permissions.TYPE_FILEVAULT: (permissions.ESCROW,),
    permissions.TYPE_LUKS: (permissions.ESCROW,),
}

GROUPS = {
    permissions.TYPE_BITLOCKER: [
        ('front-line-support', (permissions.RETRIEVE,)),
        ('developers', (permissions.SET_REGULAR,)),
        ('security-team', (permissions.SET_SILENT,)),
        ],
    permissions.TYPE_FILEVAULT: [
        ('front-line-support', (permissions.RETRIEVE,
                                permissions.CHANGE_OWNER)),
        ('developers', (permissions.SET_REGULAR,)),
        ('security-team', (permissions.SET_SILENT,)),
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
RETRIEVAL_EMAIL_SUBJECT = 'FileVault Passphrase retrieval notification.'
RETRIEVAL_EMAIL_BODY = """
The FileVault 2 encryption passphrase for your Mac has been recovered. This
passphrase allows for access to your encrypted hard disk, for example in
case you have forgotten or changed your password and cannot access it
yourself.

If you have recently contacted %(helpdesk_name)s for support, this is normal and
expected.  If not it may represent a security breach.  Please contact
%(helpdesk_name)s or forward this message to %(helpdesk_email)s so that
this event can be audited for safety and security.

Retrieved By: %(retrieved_by)s
Hostname: %(hostname)s
Platform UUID: %(platform_uuid)s
Serial Number: %(serial)s
HDD Serial: %(hdd_serial)s
Volume UUID: %(volume_uuid)s
"""