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
    this.fire(
        'iron-signal', {
          name: 'network-error',
          data: event.detail.request.status,
        });
  },

  /** @param {!Event} event */
  onResponse_: function(event) {
    let data =
        /** @type {AccessLogServerResponse_} */(event.detail.response);

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
