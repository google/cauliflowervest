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

Polymer({
  is: 'cv-retired-assets',
  properties: {
    waitingForInput_: {
      type: Boolean,
      value: true,
    },
    loading_: {
      type: Boolean,
      value: true,
    },
    queryParam_: String,
    input_: String,
    serials_: Array,

    stillActiveAssets_: {
      type: Array,
      value: function() {
        return [];
      },
    },
    retired_: {
      type: Array,
      value: function() {
        return [];
      },
    },
  },

  /** @private */
  generateRequest_: function() {
    if (!this.serials_.length) {
      this.loading_ = false;
      return;
    }
    let batch = this.serials_.splice(0, 10);
    let serials = batch.join(',');
    this.queryParam_ = encodeURIComponent(serials);

    this.$.processSerials.generateRequest();
  },

  /** @private */
  onProcessTap_: function() {
    this.waitingForInput_ = false;

    this.serials_ = this.input_.split(',').map((v) => {return v.trim();});

    this.generateRequest_();
  },

  /** @param {!Event} e */
  onResponse_: function(e) {
    this.set(
        'stillActiveAssets_',
        this.stillActiveAssets_.concat(e.detail.response['active']));
    this.set('retired_', this.retired_.concat(e.detail.response['retired']));

    if (this.serials_.length) {
      this.generateRequest_();
    } else {
      this.loading_ = false;
    }
  },

  /** @param {!Event} event */
  onNetworkError_: function(event) {
    this.fire(
        'iron-signal', {
          name: 'network-error',
          data: event.detail.request.status
        });
  },

  /**
    * @return {boolean}
    * @private
    */
  hasActiveAssetsInResult_: function() {
    return this.stillActiveAssets_.length > 0;
  },
});
