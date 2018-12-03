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

"""Module containing url handler for crons."""

import webapp2

from cauliflowervest.server.cron import group_sync
from cauliflowervest.server.cron import inventory_sync


app = webapp2.WSGIApplication([
    (r'/cron/inventory_sync', inventory_sync.InventorySync),
    (r'/cron/group_sync$', group_sync.GroupSync),
])
