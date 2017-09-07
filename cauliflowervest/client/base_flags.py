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
"""Flags that common for all clients."""
import logging



import gflags as flags

from cauliflowervest import settings as base_settings


LOGIN_TYPE_OPTIONS = 'oauth2'


flags.DEFINE_bool('debug', False, 'Enable debug mode.')
flags.DEFINE_string(
    'login_type',
    'oauth2',
    'Type of login to perform. One of: %s' % LOGIN_TYPE_OPTIONS,
)
flags.DEFINE_string(
    'server_url',
    'https://' + base_settings.SERVER_HOSTNAME,
    help='The URL where CauliflowerVest server is located (scheme + host, no path).',
)
if 'version' not in flags.FLAGS:
  flags.DEFINE_bool(
      'version', False, 'Display the version of the CauliflowerVest client.')


def HandleBaseFlags(real_main):
  """Handle --version and --debug."""
  def Wrapper(_):
    """wrap real_main."""
    options = flags.FLAGS

    if options.debug:
      logging.getLogger().setLevel(logging.DEBUG)

    if options.version:
      print 'UNKNOWN'
      return 0

    return real_main(options)

  return Wrapper
