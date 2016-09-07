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

import base64
import os
import uuid


from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import deferred
from google.appengine.ext import testbed

from google.apputils import basetest

from cauliflowervest.server import crypto
from cauliflowervest.server import models


QUEUE_NAMES = ['default', 'serial']


def SetUpTestbedTestCase(case):
  """Set up appengine testbed enviroment."""
  case.stubs = stubout.StubOutForTesting()
  case.testbed = testbed.Testbed()

  case.testbed.activate()
  # The oauth_aware decorator will 302 to login unless there is either
  # a current user _or_ a valid oauth header; this is easier to stub.
  case.testbed.setup_env(
      user_email='stub7@example.com', user_id='1234', overwrite=True)

  case.testbed.init_all_stubs()

  policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
  case.testbed.init_datastore_v3_stub(consistency_policy=policy)
  case.testbed.init_taskqueue_stub(_all_queues_valid=True)

  os.environ['AUTH_DOMAIN'] = 'example.com'

  # Lazily stub out key-fetching RPC dependency.
  def Stub(data, **_):
    return data
  case.stubs.Set(crypto, 'Decrypt', Stub)
  case.stubs.Set(crypto, 'Encrypt', Stub)


def TearDownTestbedTestCase(case):
  """Tear down appengine testbed enviroment."""
  case.stubs.UnsetAll()
  case.testbed.deactivate()


def MakeBitLockerVolume(save=True, **kwargs):
  """Put default BitlockerVolume to datastore."""
  volume_uuid = str(uuid.uuid4()).upper()
  hostname = models.BitLockerVolume.NormalizeHostname(
      volume_uuid + '.example.com')

  defaults = {
      'hostname': hostname,
      'cn': 'what',
      'dn': 'why',
      'parent_guid': '1337',
      'recovery_key': '123456789',
      'volume_uuid': volume_uuid,
      'tag': 'default',
  }
  defaults.update(kwargs)

  volume = models.BitLockerVolume(**defaults)
  if save:
    volume.put()
  return volume


def RunAllDeferredTasks(tb, queue_name=None):
  """Runs all deferred tasks in specified queue.

  If no queue is specified, then runs all deferred tasks in queues
  known to this module, in QUEUE_NAMES.

  Args:
    tb: Your test's testbed instance.
    queue_name: String. The name the queue whose tasks should be run.
  """
  if queue_name:
    queue_names = [queue_name]
  else:
    queue_names = QUEUE_NAMES

  taskqueue = tb.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

  for name in queue_names:
    tasks = taskqueue.GetTasks(name)
    for task in tasks:
      deferred.run(base64.b64decode(task['body']))
      taskqueue.DeleteTask(name, task['name'])
