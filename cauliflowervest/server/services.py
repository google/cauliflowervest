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


class InventoryService(object):
  """Default implementation."""

  def GetVolumeOwner(self, volume):
    """Gets the owner of the given volume.

    Args:
      volume: A volume entity. E.g., BitLockerVolume.

    Returns:
      A string representing the owner of the volume, if it can be found. None
      otherwise.
    """
    return volume.owner

  def GetAssetTagsFromUploadRequest(self, entity, request):
    """Gets the asset tag of the given entity during upload.

    Args:
      entity: base.BasePassphrase.
      request: Upload request.

    Returns:
      List of asset tags assosiated with entity.
    """
    return []

  def IsRetiredMac(self, serial):
    """Checks if this Mac decommissioned."""
    return False
