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
##

"""filevault module tests."""



import mox
import stubout

from django.conf import settings
settings.configure()

# pylint: disable=g-bad-import-order
import webapp2
from google.appengine.api import users
from google.appengine.ext import testbed

from google.apputils import app
from google.apputils import basetest

from cauliflowervest.server import models
from cauliflowervest.server import permissions
from cauliflowervest.server import settings
from cauliflowervest.server import util
from cauliflowervest.server.handlers import filevault as fv


class FileVaultAccessHandlerTest(mox.MoxTestBase):
  """Test the filevault.FileVault class."""

  def setUp(self):
    super(FileVaultAccessHandlerTest, self).setUp()
    self.c = fv.FileVault()

  def testCreateNewSecretEntity(self):
    result = self.c._CreateNewSecretEntity(
        'mock_owner', 'mock_volume_uuid', 'mock_secret')
    self.assertIsInstance(result, fv.models.FileVaultVolume)

  def testIsValidSecret(self):
    self.assertTrue(
        self.c.IsValidSecret('AD8C7732-6447-4EA9-B312-B438050C4988'))
    self.assertFalse(self.c.IsValidSecret('xyz'))




def main(_):
  basetest.main()


if __name__ == '__main__':
  app.run()
