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
##

"""App Engine Models for CauliflowerVest web application."""



RETRIEVE = 'retrieve'
RETRIEVE_OWN = 'retrieve_own'
RETRIEVE_CREATED_BY = 'retrieve_created_by'
ESCROW = 'escrow'
SEARCH = 'search'
MASTER = 'master'
SILENT_RETRIEVE = 'silent_retrieve'
CHANGE_OWNER = 'change_owner'

SET_REGULAR = (RETRIEVE, ESCROW, SEARCH, MASTER, CHANGE_OWNER)
SET_PROVISIONING = (RETRIEVE_CREATED_BY, SEARCH)
SET_SILENT = SET_REGULAR + (SILENT_RETRIEVE,)

TYPE_BITLOCKER = 'bitlocker'
TYPE_DUPLICITY = 'duplicity'
TYPE_FILEVAULT = 'filevault'
TYPE_LUKS = 'luks'
TYPE_PROVISIONING = 'provisioning'
TYPES = [TYPE_BITLOCKER, TYPE_DUPLICITY, TYPE_FILEVAULT, TYPE_LUKS,
         TYPE_PROVISIONING]
