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

"""Service abstraction layer."""
# pylint: disable=unused-argument
from google.appengine.ext import db


class InventoryServicePassphraseProperties(db.Model):
  """Extra properties for base.BasePassphrase.

  Contains properties that specific for IntentoryService
  """


class InventoryService(object):
  """Default implementation."""

  def GetAssetTagsFromUploadRequest(self, entity, request):
    """Gets the asset tag of the given entity during upload.

    Args:
      entity: base.BasePassphrase any Passphrase entity from datastore.
      request: Upload request.

    Raises:
      errors.AccessDeniedError
      errors.AccessError
    Returns:
      List of asset tags assosiated with entity.
    """
    return []

  def FillInventoryServicePropertiesDuringEscrow(self, entity, request):
    """Fills InventoryServicePassphraseProperties for entity.

    Args:
      entity: base.BasePassphrase.
      request: Upload request.

    Raises:
      errors.AccessDeniedError: user lacks any retrieval permissions.
      errors.AccessError: user lacks a specific retrieval permission.
    """
    return

  def IsRetiredMac(self, serial):
    """Checks if this Mac decommissioned."""
    return False

  def GetMetadataUpdates(self, entity):
    """Checks for metadata updaes.

    Args:
      entity: base.BasePassphrase.
    Returns:
      Dict containing changed property name to new value mapping.
    """
    return {}
