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
#!/usr/bin/python

"""Client main entry module."""

import getpass
import socket
import urlparse

from google.apputils import app
import gflags as flags

from cauliflowervest.client import base_client
from cauliflowervest.client import base_flags
from cauliflowervest.client.linux import client


flags.DEFINE_enum(
    'mode', 'put', ['put', 'get'],
    'Either get a passphrase given a hostname, or upload a passphrase.')
flags.DEFINE_string(
    'username', getpass.getuser(), 'User to login as.', short_name='u')

flags.DEFINE_string(
    'luks_passphrase_file', None,
    'File containing the user\'s LUKS passphrase.')
flags.DEFINE_string('hdd_serial', None, 'The hard drive serial number.')
flags.DEFINE_string(
    'platform_uuid', '', help='A UUID that will identify this machine.')
#  socket.getfqdn is a bad default, but possibly better than
# nothing.
flags.DEFINE_string(
    'hostname', socket.getfqdn(),
    'The hostname of the machine that this hdd is in.')
flags.DEFINE_string(
    'volume_uuid', None, 'The UUID for the volume we encrypted.')


@base_flags.HandleBaseFlags
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
  app.run(main)
