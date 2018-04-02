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
      observer: 'logTypeChanged_',
    },

    state: {
      type: String,
      notify: true,
      value: '',
      observer: 'stateChanged_',
    },

    start_: {
      type: String,
      observer: 'updateState_',
      value: '',
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
  },

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
    this.start_ = this.next_;
  },

  updateState_: function() {
    if (!this.logType) {
      return;
    }

    this.state = this.logType + '/' + this.start_;
  },

  logTypeChanged_: function() {
    if (this.state) {
      this.stateChanged_();
    } else {
      this.updateState_();
    }
  },

  stateChanged_: function() {
    if (!this.logType) {
      return;
    }

    let prefix = this.logType + '/';
    if (this.state.substr(0, prefix.length) != prefix) {
      this.updateState_();
      return;
    }
    this.start_ = this.state.substr(prefix.length);

    this.$.request.generateRequest();
  }
});
