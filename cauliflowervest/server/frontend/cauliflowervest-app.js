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
 *    path: (string|undefined),
 *    prefix: (string|undefined),
 * }}
 */
let AppRouteTail_;

/**
 * Root UI element.
 * @final
 * @polymer
 */
class CauliflowervestApp extends Polymer.Element {
  constructor() {
    super();

    /**
     * Page title.
     * @type {string}
     */
    this.title;

    /** @private {!AppRouteTail_} */
    this.route_ = {};

    /** @private {!AppRouteTail_} */
    this.searchState_ = {};

    /** @private {!AppRouteTail_} */
    this.retrieveState_ = {};

    /** @private {!AppRouteTail_} */
    this.logState_ = {};


    /** @private {!AppRouteTail_} */
    this.data_ = {
      mainMenuSelection: 'search',
    };
  }

  /**
   * @return {string} element identifier.
   */
  static get is() {
    return 'cauliflowervest-app';
  }

  /**
   * The properties of the Polymer element.
   * @return {!PolymerElementProperties}
   */
  static get properties() {
    return {
      title: String,
      route_: Object,
      searchState_: Object,
      retrieveState_: Object,
      logState_: Object,
      data_: Object,
    };
  }

  /** @override */
  static get observers() {
    return [
    'onPathChanged_(route_.path)'
    ];
  }

  /** @private */
  onPathChanged_() {
    if (!this.route_.path) {
      this.set('route_.path', '/search');
    }
    // wait until lazy-page initialized
    setTimeout(() => this.updateTitle_(), 20);
  }

  /** @private */
  updateTitle_() {
    if (this.data_.mainMenuSelection) {
      let page = this.root.querySelector('#' + this.data_.mainMenuSelection);
      if (goog.isDefAndNotNull(page)) {
        this.title = page.title;
        return;
      }
    }
    setTimeout(() => this.updateTitle_(), 20);
  }

  /** @private */
  openDrawer_() {
    this.$.drawerPanel.openDrawer();
  }

  /** @private */
  closeDrawer_() {
    this.$.drawerPanel.closeDrawer();
  }

  /** @private */
  resetSubstate_() {
    this.set('searchState_.path', '');
    this.set('logState_.path', '');
    this.set('retrieveState_.path', '');
  }

  /**
   * @param {!CustomEvent} event
   * @private
   */
  onNetworkError_(event) {
    if (event.detail.data == 403) {
      this.$.accessDeniedDialog.open();
    } else {
      this.$.networkErrorDialog.open();
    }
  }
}

customElements.define(CauliflowervestApp.is, CauliflowervestApp);
