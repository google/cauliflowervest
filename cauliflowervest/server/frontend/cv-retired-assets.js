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
 * Provides a way to batch retrieve passwords for retired assets.
 * @final
 * @polymer
 */
class CvRetiredAssets extends Polymer.Element {
  constructor() {
    super();

    /** @private {boolean} */
    this.waitingForInput_ = true;

    /** @private {boolean} */
    this.loading_ = true;

    /** @private {string} */
    this.queryParam_;

    /** @private {string} */
    this.input_;

    /** @private {?Array} */
    this.serials_;

    /** @private {!Array<string>} */
    this.stillActiveAssets_ = [];

    /** @private {!Array<string>} */
    this.retired_ = [];
  }

  /**
   * @return {string} element identifier.
   */
  static get is() {
    return 'cv-retired-assets';
  }

  /**
   * The properties of the Polymer element.
   * @return {!PolymerElementProperties}
   */
  static get properties() {
    return {
      waitingForInput_: Boolean,
      loading_: Boolean,
      queryParam_: String,
      input_: String,
      serials_: Array,
      stillActiveAssets_: Array,
      retired_: Array,
    };
  }

  /** @private */
  generateRequest_() {
    if (!this.serials_.length) {
      this.loading_ = false;
      return;
    }
    let batch = this.serials_.splice(0, 10);
    let serials = batch.join(',');
    this.queryParam_ = encodeURIComponent(serials);

    this.$.processSerials.generateRequest();
  }

  /** @private */
  onProcessTap_() {
    this.waitingForInput_ = false;

    this.serials_ = this.input_.split(',').map((v) => {return v.trim();});

    this.generateRequest_();
  }

  /**
   * @param {!Event} e
   * @private
   */
  onResponse_(e) {
    this.set(
        'stillActiveAssets_',
        this.stillActiveAssets_.concat(e.detail.response['active']));
    this.set('retired_', this.retired_.concat(e.detail.response['retired']));

    if (this.serials_.length) {
      this.generateRequest_();
    } else {
      this.loading_ = false;
    }
  }

  /**
   * @param {!Event} event
   * @private
   */
  onNetworkError_(event) {
    this.dispatchEvent(new CustomEvent(
        'cv-network-error', {
          detail: {data: event.detail.request.status},
          bubbles: true,
          composed: true,
       }));
  }

  /**
    * @return {boolean}
    * @private
    */
  hasActiveAssetsInResult_() {
    return this.stillActiveAssets_.length > 0;
  }
}

customElements.define(CvRetiredAssets.is, CvRetiredAssets);
