#!/usr/bin/env python
#
# Copyright 2015 Google Inc. All Rights Reserved.
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
#"""duplicity handler tests."""

import mox
import stubout

from django.conf import settings
settings.configure()

from google.apputils import basetest

from cauliflowervest.server.handlers import duplicity

VALID_UUID = 'ca7d099cb7a811e2b7a0ac162d075011'
INVALID_UUID = 'This is not a valid UUID, at all!'


class DuplicityRequestHandlerTest(mox.MoxTestBase):
  """Test the duplicity.Duplicity class."""

  def setUp(self):
    super(DuplicityRequestHandlerTest, self).setUp()
    self.c = duplicity.Duplicity()

  def testCreateNewSecretEntity(self):
    result = self.c._CreateNewSecretEntity(
        'mock_owner', 'mock_volume_uuid', 'mock_secret')
    self.assertIsInstance(result, duplicity.models.DuplicityKeyPair)


if __name__ == '__main__':
  basetest.main()
