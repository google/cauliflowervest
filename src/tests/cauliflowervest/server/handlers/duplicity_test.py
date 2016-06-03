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
"""duplicity handler tests."""


from google.apputils import basetest

from cauliflowervest.server.handlers import duplicity
from tests.cauliflowervest.server.handlers import test_util


class DuplicityRequestHandlerTest(basetest.TestCase):
  """Test the duplicity.Duplicity class."""

  def setUp(self):
    super(DuplicityRequestHandlerTest, self).setUp()

    test_util.SetUpTestbedTestCase(self)

    self.c = duplicity.Duplicity()

  def tearDown(self):
    super(DuplicityRequestHandlerTest, self).tearDown()
    test_util.TearDownTestbedTestCase(self)

  def testCreateNewSecretEntity(self):
    result = self.c._CreateNewSecretEntity(
        'mock_owner', 'mock_volume_uuid', 'mock_secret')
    self.assertIsInstance(result, duplicity.models.DuplicityKeyPair)
    # check that _CreateNewSecretEntity did not put new entity into datastore
    self.assertEqual(0, len(duplicity.models.DuplicityKeyPair.all().fetch(10)))


if __name__ == '__main__':
  basetest.main()
