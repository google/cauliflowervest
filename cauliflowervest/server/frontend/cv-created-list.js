// Copyright 2017 Google Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * List of volumes created by current user.
 */
Polymer({
  is: 'cv-created-list',
  properties: {
    loading_: {
      type: Boolean,
      value: true,
    },
    volumes_: {
      type: Array,
      notify: true,
      value: function() {
        return [];
      }
    }
  },

  /** @param {!Event} event */
  onNetworkError_: function(event) {
    this.fire('cv-network-error', {data: event.detail.request.status});
  },
});
