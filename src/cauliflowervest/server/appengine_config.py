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

"""appengine_config.py module for CauliflowerVest."""


# pylint: disable=unused-import
# Importing these modules before some (what?) import path mangling happens
# somewhere else makes things not fail on the dev_appserver.
# Also, provide compatibilty for the entire keyczar tar or solely the src dir.
try:
  from keyczar.src.keyczar import keyczar
  from keyczar.src.keyczar import keyinfo
  from keyczar.src.keyczar import readers
except ImportError:
  from keyczar import keyczar
  from keyczar import keyinfo
  from keyczar import readers