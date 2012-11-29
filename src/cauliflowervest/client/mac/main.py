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



import logging
import optparse
import sys


from cauliflowervest import settings as base_settings
from cauliflowervest.client.mac import corestorage
from cauliflowervest.client.mac import tkinter

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
    '--no_welcome', dest='no_welcome',
    help='Suppress welcome message.',
    action='store_true', default=False)
PARSER.add_option(
    '--server_url', dest='server_url',
    help='The URL where CauliflowerVest server is located (scheme + host, no path).',
    default='https://' + base_settings.SERVER_HOSTNAME)
PARSER.add_option(
    '-v', '-V', '--version', action='store_true', dest='version',
    help='Display the version of the CauliflowerVest client.'
    )
options, unused_sysv = PARSER.parse_args()


def main():
  if options.debug:
    logging.getLogger().setLevel(logging.DEBUG)

  if options.version:
    print 'UNKNOWN'
    return 0

  if options.login_type == 'clientlogin':
    gui = tkinter.GuiClientLogin(options.server_url)
  else:
    raise NotImplementedError('Unsupported login type: %s', options.login_type)

  _, encrypted_volumes, _ = corestorage.GetStateAndVolumeIds()
  try:
    if encrypted_volumes:
      gui.EncryptedVolumePrompt()
    else:
      gui.PlainVolumePrompt(options.no_welcome)
  except Exception as e:  # pylint: disable-msg=W0703
    gui.ShowFatalError(e)
    return 1

  return 0


if __name__ == '__main__':
  sys.exit(main())