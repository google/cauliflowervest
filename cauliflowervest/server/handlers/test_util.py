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

"""General purpose test utilities."""

import base64
import os
import uuid


import mock

from google.appengine.ext import deferred
from google.appengine.ext import testbed

from common.testing import basetest
from cauliflowervest.server import crypto
from cauliflowervest.server.models import firmware
from cauliflowervest.server.models import volumes


QUEUE_NAMES = ['default', 'serial', 'cron']


class BaseTest(basetest.AppEngineTestCase):
  """Base test class for all tests."""

  def setUp(self):
    super(BaseTest, self).setUp()
    self.Login('stub7@example.com', user_id='1234')

    os.environ['AUTH_DOMAIN'] = 'example.com'

    # Lazily stub out key-fetching RPC dependency.
    def Stub(data, **_):
      return data
    self.patches = [
        mock.patch.object(crypto, 'Decrypt', side_effect=Stub),
        mock.patch.object(crypto, 'Encrypt', side_effect=Stub),
    ]
    for m in self.patches:
      m.start()

  def tearDown(self):
    for m in self.patches:
      m.stop()

    super(BaseTest, self).tearDown()


def MakeBitLockerVolume(save=True, **kwargs):
  """Put default BitlockerVolume to datastore."""
  volume_uuid = str(uuid.uuid4()).upper()
  hostname = volumes.BitLockerVolume.NormalizeHostname(
      volume_uuid + '.example.com')

  defaults = {
      'hostname': hostname,
      'cn': 'what',
      'dn': 'why',
      'parent_guid': '1337',
      'recovery_key': '123456789',
      'volume_uuid': volume_uuid,
      'tag': 'default',
      'recovery_guid': 'guid123',
  }
  defaults.update(kwargs)

  volume = volumes.BitLockerVolume(**defaults)
  if save:
    volume.put()
  return volume


def MakeFileVaultVolume(save=True, **kwargs):
  """Create and return a FileVaultVolume."""
  defaults = {
      'hdd_serial': 'blah',
      'passphrase': '123456789',
      'volume_uuid': str(uuid.uuid4()).upper(),
      'owner': 'someone',
      'serial': 'foo',
      'platform_uuid': 'bar',
  }
  defaults.update(kwargs)

  volume = volumes.FileVaultVolume(**defaults)
  if save:
    volume.put()
  return volume


def MakeAppleFirmware(save=True, **kwargs):
  """Create and return a AppleFirmware for test."""
  defaults = {
      'serial': 'blah',
      'password': '123456789',
      'platform_uuid': str(uuid.uuid4()).upper(),
      'owner': 'someone',
      'asset_tags': ['12345'],
      'hostname': 'zerocool.example.com',
  }
  defaults.update(kwargs)

  entity = firmware.AppleFirmwarePassword(**defaults)
  if save:
    entity.put()
  return entity


def MakeLinuxFirmware(save=True, **kwargs):
  """Create and return a LinuxFirmware for test."""
  defaults = {
      'manufacturer': 'Lonovo',
      'serial': 'blah',
      'password': '123456789',
      'machine_uuid': str(uuid.uuid4()).upper(),
      'owner': 'someone',
      'asset_tags': ['12345'],
      'hostname': 'zerocool.example.com',
  }
  defaults.update(kwargs)

  entity = firmware.LinuxFirmwarePassword(**defaults)
  if save:
    entity.put()
  return entity


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
    try:
      tasks = taskqueue.GetTasks(name)
      for task in tasks:
        deferred.run(base64.b64decode(task['body']))
        taskqueue.DeleteTask(name, task['name'])
    except KeyError:
      # If a queue hasn't had a task added to it then we'll get a harmless
      # keyerror when trying to get any tasks that have been added to it.
      pass
