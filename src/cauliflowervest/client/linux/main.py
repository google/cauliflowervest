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
##

"""CauliflowerVest client main entry module."""



import getpass
import optparse
import socket
import sys
import urlparse

from cauliflowervest.client import base_client
from cauliflowervest.client.linux import client


PARSER = optparse.OptionParser()
base_client.PARSER.add_option(
    '--mode', dest='mode',
    choices=['put', 'get'],
    help='Either get a passphrase given a hostname, or upload a passphrase.'
    )
base_client.PARSER.add_option(
    '--username', dest='username', default=getpass.getuser(),
    help='User to login as.'
    )
base_client.PARSER.add_option(
    '--luks_passphrase_file', dest='luks_passphrase_file',
    help='File containing the user\'s LUKS passphrase.'
    )
base_client.PARSER.add_option(
    '--hdd_serial', dest='hdd_serial',
    help='The hard drive serial number.'
    )
base_client.PARSER.add_option(
    '--platform_uuid', dest='platform_uuid',
    help='A UUID that will identify this machine.'
    )
# TODO(user): socket.getfqdn is a bad default, but possibly better than
# nothing.
base_client.PARSER.add_option(
    '--hostname', dest='hostname', default=socket.getfqdn(),
    help='The hostname of the machine that this hdd is in.'
    )
base_client.PARSER.add_option(
    '--volume_uuid', dest='volume_uuid',
    help='The UUID for the volume we encrypted.'
    )


def main(options):
  if options.login_type == 'oauth2':
    credentials = base_client.GetOauthCredentials()
    opener = base_client.BuildOauth2Opener(credentials)
  else:
    raise NotImplementedError('Unsupported login type: %s', options.login_type)

  c = client.LuksClient(options.server_url, opener)

  if options.mode == 'put':
    luks_passphrase = open(options.luks_passphrase_file, 'r').read().strip()
    data = {
        'hostname': options.hostname,
        'hdd_serial': options.hdd_serial,
        'platform_uuid': options.platform_uuid,
        'owner': options.username
        }
    c.UploadPassphrase(options.volume_uuid, luks_passphrase, data)
  if options.mode == 'get':
    print c.RetrieveSecret(options.volume_uuid)


if __name__ == '__main__':
  sys.exit(base_client.main(main))
