goog.provide('cauliflowervest.AccessLog');


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
cauliflowervest.AccessLog = Polymer({
  is: 'cv-access-log',
  properties: {
    logType: {
      type: String,
      observer: 'updateLogType_',
    },
    state: {
      type: String,
      notify: true,
      value: '',
      observer: 'parseState_',
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

  /** @param {!Event} e */
  handleNetworkError_: function(e) {
    this.fire(
        'iron-signal', {name: 'network-error', data: e.detail.request.status});
  },

  /** @param {!Event} e */
  handleResponse_: function(e) {
    var data =
        /** @type {AccessLogServerResponse_} */(e.detail.response);

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

  updateLogType_: function() {
    if (this.state) {
      this.parseState_();
    } else {
      this.updateState_();
    }
  },

  parseState_: function() {
    if (!this.logType) {
      return;
    }

    var prefix = this.logType + '/';
    if (this.state.substr(0, prefix.length) != prefix) {
      this.updateState_();
      return;
    }
    this.start_ = this.state.substr(prefix.length);

    this.$.request.generateRequest();
  }
});
