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
 *    mtime: string,
 *    user: string,
 *    message: string,
 *    successful: string,
 *    query: string,
 * }}
 */
let LogEntry_;


/**
 * Server response to /logs.
 * @typedef {{
 *    logs: !Array<!LogEntry_>,
 *    start_next: string,
 * }}
 */
let AccessLogServerResponse_;


/**
 * Table with log entries for volume type.
 * @polymer
 */
class CvAccessLog extends Polymer.Element {
  constructor() {
    super();

    /** @type {string} */
    this.logType;

    /**
     * State saved as part of url.
     * logType/pageToken/showOnlyErrors
     * @type {string}
     */
    this.state = '';

    /** @type {string} */
    this.next = '';

    /** @private {boolean} */
    this.loading_ = true;

    /** @private {!Array<!LogEntry_>} */
    this.logs_ = [];

    /** @private {boolean} */
    this.blockUpdateState_ = false;

    /** @private {{start: string, showOnlyErrors: boolean}} */
    this.parsedState_ = {
      start: '',
      showOnlyErrors: false,
    };
  }

  /**
   * @return {string} element identifier.
   */
  static get is() {
    return 'cv-access-log';
  }

  /**
   * The properties of the Polymer element.
   * @return {!PolymerElementProperties}
   */
  static get properties() {
    return {
      logType: String,
      state: {
        type: String,
        notify: true,
      },
      parsedState_: Object,
      next_: String,
      loading_: Boolean,
      logs_: Array,
      blockUpdateState_: Boolean,
    };
  }

  /** @override */
  static get observers() {
    return [
      'updateState_(parsedState_.start, parsedState_.showOnlyErrors)',
      'stateChanged_(logType, state)',
    ];
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
   * @param {!Event} event
   * @private
   */
  onResponse_(event) {
    const data =
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
  }

  /** @private */
  showNextPage_() {
    this.loading_ = true;
    this.set('parsedState_.start', this.next_);
  }

  /** @private */
  updateState_() {
    if (!this.logType || this.blockUpdateState_) {
      return;
    }

    let state = this.logType + '/' + this.parsedState_.start;
    if (this.parsedState_.showOnlyErrors) {
      state += '/1';
    }

    this.state = state;
  }

  /**
   * @param {string} logType
   * @param {string} componentState
   * @private
   */
  stateChanged_(logType, componentState) {
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
}

customElements.define(CvAccessLog.is, CvAccessLog);
