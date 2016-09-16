#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
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
"""CauliflowerVest client main entry module."""

import os
import pwd
import sys

from cauliflowervest.client import base_client
from cauliflowervest.client.mac import corestorage
from cauliflowervest.client.mac import tkinter


base_client.PARSER.add_option(
    '--no_welcome', dest='no_welcome',
    help='Suppress welcome message.',
    action='store_true', default=False)
base_client.PARSER.add_option(
    '-u', '-U', '--username', action='store', dest='username', type='string',
    help='Username to use by default.')


def main(options):
  if options.login_type == 'oauth2':
    if options.username:
      username = options.username
    else:
      username = pwd.getpwuid(os.getuid()).pw_name
    gui = tkinter.GuiOauth(options.server_url, username)
  else:
    raise NotImplementedError('Unsupported login type: %s', options.login_type)

  _, encrypted_volumes, _ = corestorage.GetStateAndVolumeIds()
  try:
    if encrypted_volumes:
      gui.EncryptedVolumePrompt()
    else:
      gui.PlainVolumePrompt(options.no_welcome)
  except Exception as e:  # pylint: disable=broad-except
    gui.ShowFatalError(e)
    return 1

  return 0


if __name__ == '__main__':
  sys.exit(base_client.main(main))
