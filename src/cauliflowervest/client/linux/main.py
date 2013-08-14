#!/usr/bin/env python
# 
# Copyright 2012 Google Inc. All Rights Reserved.
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



import getpass
import logging
import optparse
import socket
import sys
import urlparse


from cauliflowervest import settings as base_settings
from cauliflowervest.client import base_client
from cauliflowervest.client.linux import client

LOGIN_TYPE_OPTIONS = 'clientlogin'

PARSER = optparse.OptionParser()
PARSER.add_option(
    '--debug', dest='debug',
    help='Enable debug mode.',
    action='store_true', default=False)
PARSER.add_option(
    '--login_type', dest='login_type',
    help='Type of login to perform. One of: %s' % LOGIN_TYPE_OPTIONS,
    default='clientlogin'
    )
PARSER.add_option(
    '--mode', dest='mode',
    choices=['put', 'get'],
    help='Either get a passphrase given a hostname, or upload a passphrase.'
    )
PARSER.add_option(
    '--username', dest='username', default=getpass.getuser(),
    help='User to login as.'
    )
PARSER.add_option(
    '--password_file', dest='password_file',
    help='File containing the user\'s password.'
    )
PARSER.add_option(
    '--luks_passphrase_file', dest='luks_passphrase_file',
    help='File containing the user\'s LUKS passphrase.'
    )
PARSER.add_option(
    '--hdd_serial', dest='hdd_serial',
    help='The hard drive serial number.'
    )
PARSER.add_option(
    '--platform_uuid', dest='platform_uuid',
    help='A UUID that will identify this machine.'
    )
# TODO(user): socket.getfqdn is a bad default, but possibly better than
# nothing.
PARSER.add_option(
    '--hostname', dest='hostname', default=socket.getfqdn(),
    help='The hostname of the machine that this hdd is in.'
    )
PARSER.add_option(
    '--volume_uuid', dest='volume_uuid',
    help='The UUID for the volume we encrypted.'
    )
PARSER.add_option(
    '--server_url', dest='server_url',
    help='The URL where CauliflowerVest server is located (scheme + host, no path).',
    default='https://' + base_settings.SERVER_HOSTNAME)
options, unused_sysv = PARSER.parse_args()


def main():
  if options.debug:
    logging.getLogger().setLevel(logging.DEBUG)

  if options.version:
    return 0

  password = open(options.password_file, 'r').read().strip()
  luks_passphrase = open(options.luks_passphrase_file, 'r').read().strip()
  hostname = urlparse.urlparse(options.server_url)[1]
  if options.login_type == 'clientlogin':
    credentials = (options.username, password)
    opener = base_client.BuildClientLoginOpener(hostname, credentials)
  else:
    raise NotImplementedError()

  metadata = {
      'hostname': options.hostname,
      'hdd_serial': options.hdd_serial,
      'platform_uuid': options.platform_uuid,
      'owner': options.username
      }

  c = client.LuksClient(options.server_url, opener)
  if options.mode == 'put':
    c.UploadPassphrase(options.volume_uuid, luks_passphrase, metadata)
  if options.mode == 'get':
    print c.RetrieveSecret(options.volume_uuid)


if __name__ == '__main__':
  sys.exit(main())