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
 * Various maintenance actions.
 * @polymer
 */
class CvAdminPage extends Polymer.Element {
  constructor() {
    super();

    /** @type {string} */
    this.state = '/admin/';

    /** @private {string} */
    this.xsrfToken_;
  }

  /**
   * @return {string} element identifier.
   */
  static get is() {
    return 'cv-admin-page';
  }

  /**
   * The properties of the Polymer element.
   * @return {!PolymerElementProperties}
   */
  static get properties() {
    return {
      state: String,
      xsrfToken_: String,
    };
  }

  /**
   * @param {!Event} event
   * @private
   */
  onResponse_(event) {
    this.xsrfToken_ = event.detail.response;

    this.$.dataRequest.generateRequest();
  }

  /** @private */
  onClick_() {
    this.$.tokenRequest.generateRequest();
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
}

customElements.define(CvAdminPage.is, CvAdminPage);
