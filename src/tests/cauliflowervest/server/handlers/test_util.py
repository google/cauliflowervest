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
"""General purpose test utilities."""

import os

from google.appengine.ext import testbed

from cauliflowervest.server import crypto


def SetUpTestbedTestCase(case):
  """Set up appengine testbed enviroment."""
  case.testbed = testbed.Testbed()

  # The oauth_aware decorator will 302 to login unless there is either
  # a current user _or_ a valid oauth header; this is easier to stub.
  case.testbed.setup_env(
      user_email='stub7@example.com', user_id='1234', overwrite=True)

  case.testbed.activate()
  case.testbed.init_all_stubs()
  os.environ['AUTH_DOMAIN'] = 'example.com'

  # Lazily stub out key-fetching RPC dependency.
  crypto.Decrypt = lambda x: x
  crypto.Encrypt = lambda x: x


def TearDownTestbedTestCase(case):
  """Tear down appengine testbed enviroment."""
  case.testbed.deactivate()
