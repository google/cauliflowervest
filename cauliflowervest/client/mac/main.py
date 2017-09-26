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
"""CauliflowerVest client main entry module."""

import os
import pwd

from absl import app
from absl import flags
from cauliflowervest.client import base_flags
from cauliflowervest.client.mac import glue
from cauliflowervest.client.mac import tkinter


flags.DEFINE_bool(
    'welcome', True,
    'Show welcome message.')
flags.DEFINE_string(
    'username', None, 'Username to use by default.', short_name='u')


@base_flags.HandleBaseFlags
def main(options):
  if options.username:
    username = options.username
  else:
    username = pwd.getpwuid(os.getuid()).pw_name
  if options.login_type == 'oauth2':
    gui = tkinter.GuiOauth(options.server_url, username)
  
  else:
    raise NotImplementedError('Unsupported login type: %s', options.login_type)

  storage = glue.GetStorage()
  if not storage:
    gui.ShowFatalError('Could not determine File System type')
    return 1
  _, encrypted_volumes, _ = storage.GetStateAndVolumeIds()
  try:
    if encrypted_volumes:
      gui.EncryptedVolumePrompt()
    else:
      gui.PlainVolumePrompt(options.welcome)
  except Exception as e:  # pylint: disable=broad-except
    gui.ShowFatalError(e)
    return 1

  return 0


if __name__ == '__main__':
  app.run()
