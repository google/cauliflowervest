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

"""App Engine Models for CauliflowerVest web application."""



RETRIEVE = 'retrieve'
ESCROW = 'escrow'
SEARCH = 'search'
MASTER = 'master'
SILENT_RETRIEVE = 'silent_retrieve'

SET_REGULAR = set([RETRIEVE, ESCROW, SEARCH, MASTER])
SET_SILENT = set(list(SET_REGULAR) + [SILENT_RETRIEVE])

TYPE_BITLOCKER = 'bitlocker'
TYPE_FILEVAULT = 'filevault'
TYPES = [TYPE_BITLOCKER, TYPE_FILEVAULT]