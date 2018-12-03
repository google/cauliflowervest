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
 * @typedef {{
 *    hostname: string,
 *    passphrase: string,
 *    created: string,
 * }}
 */
let CreatesListEntry_;

/**
 * List of volumes created by current user.
 * @final
 * @polymer
 */
class CvCreatedList extends Polymer.Element {
  constructor() {
    super();

    /** @private {boolean} */
    this.loading_ = true;

    /** @private {!Array<!CreatesListEntry_>} */
    this.volumes_ = [];
  }

  /**
   * @return {string} element identifier.
   */
  static get is() {
    return 'cv-created-list';
  }

  /**
   * The properties of the Polymer element.
   * @return {!PolymerElementProperties}
   */
  static get properties() {
    return {
      loading_: Boolean,
      volumes_: {
        type: Array,
        notify: true,
      }
    };
  }

  /**
   * @param {!CustomEvent} event
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
}

customElements.define(CvCreatedList.is, CvCreatedList);
