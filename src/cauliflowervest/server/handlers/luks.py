#!/usr/bin/env python
# 
# Copyright 2012 Google Inc. All Rights Reserved.
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

"""Module to handle interaction with a Luks key."""

from cauliflowervest.server import handlers
from cauliflowervest.server import models


class Luks(handlers.LuksAccessHandler):
  """Handler for /luks URL."""

  def _CreateNewSecretEntity(self, owner, volume_uuid, secret):
    return models.LuksVolume(
        key_name=volume_uuid,
        owner=owner,
        volume_uuid=volume_uuid,
        passphrase=str(secret))

  def VerifyEscrow(self, volume_uuid):
    """Handles a GET to verify if a volume uuid has an escrowed passphrase."""
    # NOTE(user): In production, we have seen UUIDs with a trailing /
    volume_uuid = volume_uuid.rstrip('/')
    return super(Luks, self).VerifyEscrow(volume_uuid)
