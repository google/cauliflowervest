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

"""Various error classes."""
import httplib


class Error(Exception):
  """Class for domain specific exceptions."""
  error_code = httplib.BAD_REQUEST


class AccessError(Error):
  """There was an error accessing a passphrase or key."""


class NotFoundError(AccessError):
  """No passphrase was found."""
  error_code = httplib.NOT_FOUND


class DuplicateEntity(Error):
  """New entity is a duplicate of active passphrase with same target_id."""


class AccessDeniedError(AccessError):
  """Accessing a passphrase was denied."""
  error_code = httplib.FORBIDDEN


class InternalServerError(Error):
  """There was an internal server error encountered during processing."""
  error_code = httplib.INTERNAL_SERVER_ERROR
