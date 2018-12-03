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
 * Page responsible for displaying all types of logs.
 * @polymer
 */
class CvLogsPage extends Polymer.Element {
  constructor() {
    super();
    /** @type {string} */
    this.state;

    /** @const {string} */
    this.title;

    /** @private {string} */
    this.route_;

    /** @private {string} */
    this.createdState_ = 'created/';

    /** @private {string} */
    this.luksState_ = '';

    /** @private {string} */
    this.bitlockerState_ = '';

    /** @private {string} */
    this.provisioningState_ = '';

    /** @private {string} */
    this.filevaultState_ = '';

    /** @private {string} */
    this.apple_firmwareState_ = '';

    /** @private {string} */
    this.linux_firmwareState_ = '';

    /** @private {boolean} */
    this.initialized_ = true;
  }

  /**
   * @return {string} element identifier.
   */
  static get is() {
    return 'cv-logs-page';
  }

  /**
   * The properties of the Polymer element.
   * @return {!PolymerElementProperties}
   */
  static get properties() {
    return {
      state: {
        type: String,
        notify: true,
        observer: 'stateChanged_'
      },
      title: {
        type: String,
        readOnly: true,
        value: 'Access Logs',
      },
      route_: {
        type: String,
        observer: 'updateState_',
      },
      createdState_: String,
      luksState_: {
        type: String,
        observer: 'updateState_',
      },
      bitlockerState_: {
        type: String,
        observer: 'updateState_',
      },
      provisioningState_: {
        type: String,
        observer: 'updateState_',
      },
      filevaultState_: {
        type: String,
        observer: 'updateState_',
      },
      apple_firmwareState_: {
        type: String,
        observer: 'updateState_',
      },
      linux_firmwareState_: {
        type: String,
        observer: 'updateState_',
      },
    };
  }

  /** @override */
  connectedCallback() {
    super.connectedCallback();
    if (!this.route_) {
      this.route_ = 'created';
    }
  }

  /**
   * @param {string} state
   * @private
   */
  stateChanged_(state) {
    state = state.substr(1);
    let values = ['created', 'bitlocker', 'filevault', 'luks', 'provisioning', 'apple_firmware', 'linux_firmware'];
    for (let i = 0; i < values.length; i++) {
      let t = values[i] + '/';
      if (state.substr(0, t.length) == t) {
        this.route_ = values[i];
        this.set(values[i] + 'State_', state);
        break;
      }
    }
  }

  /** @private */
  updateState_() {
    if (!this.initialized_) {
      return;
    }
    // filter uninitilized components
    let substate = this.get(this.route_ + 'State_');
    if (!goog.isString(substate) || substate.length == 0) {
      return;
    }

    this.state = '/' + substate;
  }
}

customElements.define(CvLogsPage.is, CvLogsPage);
