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
 * Server response to /logs.
 * @typedef {{
 *    logs: !Array,
 *    start_next: string,
 * }}
 */
var AccessLogServerResponse_;


/**
 * Table with log entries for volume type.
 */
Polymer({
  is: 'cv-access-log',
  properties: {
    logType: {
      type: String,
    },

    /**
     * State saved as part of url.
     * logType/pageToken/showOnlyErrors
     */
    state: {
      type: String,
      notify: true,
      value: '',
    },

    /**
     * @private {{start: string, showOnlyErrors: boolean}}
     */
    parsedState_: {
      type: Object,
      value: function() {
        return {
          start: '',
          showOnlyErrors: false,
        };
      },
    },

    next_: {
      type: String,
      value: '',
    },

    loading_: {
      type: Boolean,
      value: true,
    },

    logs_: {
      type: Array,
      value: function() {
        return [];
      }
    },

    blockUpdateState_: {
      type: Boolean,
      value: false,
    },
  },
  observers: [
    'updateState_(parsedState_.start, parsedState_.showOnlyErrors)',
    'stateChanged_(logType, state)',
  ],

  /** @param {!Event} event */
  onNetworkError_: function(event) {
    this.fire('cv-network-error', {data: event.detail.request.status});
  },

  /** @param {!Event} event */
  onResponse_: function(event) {
    let data =
        /** @type {AccessLogServerResponse_} */(event.detail.response);

    for (let entry of data.logs) {
      let date = new Date(entry['mtime']);
      entry['mtime'] = date.toLocaleDateString() + ' ' +
          date.toLocaleTimeString();
    }
    this.logs_ = data.logs;
    if (data.start_next) {
      this.next_ = encodeURIComponent(data.start_next);
    } else {
      this.next_ = '';
    }
  },

  showNextPage_: function() {
    this.loading = true;
    this.set('parsedState_.start', this.next_);
  },

  updateState_: function() {
    if (!this.logType || this.blockUpdateState_) {
      return;
    }

    let state = this.logType + '/' + this.parsedState_.start;
    if (this.parsedState_.showOnlyErrors) {
      state += '/1';
    }

    this.state = state;
  },

  /**
   * @param {string} logType
   * @param {string} componentState
   * @private
   */
  stateChanged_: function(logType, componentState) {
    if (!logType) {
      return;
    }

    let state = componentState.split('/');
    if (state[0] != this.logType) {
      this.updateState_();
      return;
    }

    this.parsedState_ = {
      start: state.length > 1 ? state[1] : '',
      showOnlyErrors: state.length > 2 ? state[2] == '1' : this.parsedState_.showOnlyErrors,
    };

    this.$.request.generateRequest();
  }
});
