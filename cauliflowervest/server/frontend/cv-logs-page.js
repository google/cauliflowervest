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
 */
Polymer({
  is: 'cv-logs-page',
  properties: {
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

    createdState_: {
      type: String,
      value: 'created/',
    },

    luksState_: {
      type: String,
      observer: 'updateState_',
      value: '',
    },

    bitlockerState_: {
      type: String,
      observer: 'updateState_',
      value: '',
    },

    provisioningState_: {
      type: String,
      observer: 'updateState_',
      value: '',
    },

    filevaultState_: {
      type: String,
      observer: 'updateState_',
      value: '',
    },

    apple_firmwareState_: {
      type: String,
      observer: 'updateState_',
      value: '',
    },

    linux_firmwareState_: {
      type: String,
      observer: 'updateState_',
      value: '',
    },
  },

  /** @override */
  attached: function() {
    if (!this.route_) {
      this.route_ = 'created';
    }
  },

  /**
   * @param {string} state
   */
  stateChanged_: function(state) {
    state = state.substr(1);
    let values = ['created', 'bitlocker', 'filevault', 'luks', 'provisioning', 'apple_firmware', 'linux_firmware'];
    for (let i = 0; i < values.length; i++) {
      let t = values[i] + '/';
      if (state.substr(0, t.length) == t) {
        this.route_ = values[i];
        this[values[i] + 'State_'] = state;
        break;
      }
    }
  },

  updateState_: function() {
    // filter uninitilized components
    let substate = this[this.route_ + 'State_'];
    if (!goog.isString(substate) || substate.length == 0) {
      return;
    }

    this.state = '/' + substate;
  },
});
