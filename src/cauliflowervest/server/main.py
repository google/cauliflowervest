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
# #

"""Main module for CauliflowerVest including wsgi URL mappings."""




import appengine_config
from google.appengine import api
from google.appengine import runtime
from cauliflowervest.server import urls


# TODO(user): we have a main module like this in other products to catch
#   exceptions and appropriate log/notify users.  However I don't think I've
#   seen it trigger at all since we moved to HRD.  Do we need/want this
#   here?


def main():
  try:
    urls.main()
  except (
      api.datastore_errors.Timeout,
      api.datastore_errors.InternalError,
      runtime.apiproxy_errors.CapabilityDisabledError):
    pass
    # TODO(user): email? extra logging? ...


if __name__ == '__main__':
  main()