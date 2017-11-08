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


/** Various maintenance actions. */
Polymer({
  is: 'cv-admin-page',
  properties: {
    state: {
      type: String,
      value: '/admin/',
    },

    xsrfToken_: String,
  },

  /** @param {!Event} event */
  onResponse_: function(event) {
    this.xsrfToken_ = event.detail.response;

    this.$.dataRequest.generateRequest();
  },

  onClick_: function() {
    this.$.tokenRequest.generateRequest();
  },

  /** @param {!Event} event */
  onNetworkError_: function(event) {
    this.fire(
        'iron-signal', {
          name: 'network-error',
          data: event.detail.request.status
        });
  },
});
