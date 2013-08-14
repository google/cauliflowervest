#!/usr/bin/env python
# 
# Copyright 2013 Google Inc. All Rights Reserved.
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
# """search module tests."""



import os
import mox
import stubout

from django.conf import settings
settings.configure()

from google.apputils import app
from google.apputils import basetest

from cauliflowervest.server.handlers import search


class SearchModuleTest(mox.MoxTestBase):
  """Test the search module."""

  def setUp(self):
    mox.MoxTestBase.setUp(self)
    os.environ['AUTH_DOMAIN'] = 'example.com'

  def tearDown(self):
    self.mox.UnsetStubs()

  def _HostnameSearchHelper(self, hostname):
    mock_model = self.mox.CreateMockAnything()
    mock_model.all().AndReturn(mock_model)
    mock_model.filter('hostname =', hostname)
    result = self.mox.CreateMockAnything()
    result.created = ''  # used for sorting.
    mock_model.fetch(999).AndReturn([result])
    return mock_model


  def testVolumesForQueryHostname(self):
    hostname = 'FOOHOST'
    query = 'hostname:%s' % hostname
    mock_model = self._HostnameSearchHelper(hostname)
    self.mox.ReplayAll()
    search.VolumesForQuery(query, mock_model, False)
    self.mox.VerifyAll()

  def testVolumesForQueryCreatedBy(self):
    created_by = 'foouser'
    query = 'created_by:%s' % created_by
    email = '%s@%s' % (created_by, os.environ['AUTH_DOMAIN'])

    created_by_user = search.users.User(email)

    mock_model = self.mox.CreateMockAnything()
    mock_model.all().AndReturn(mock_model)
    mock_model.filter('created_by =', created_by_user)
    result = self.mox.CreateMockAnything()
    result.created = ''  # used for sorting.
    mock_model.fetch(999).AndReturn([result])

    self.mox.ReplayAll()
    search.VolumesForQuery(query, mock_model, False)
    self.mox.VerifyAll()


def main(_):
  basetest.main()


if __name__ == '__main__':
  app.run()