goog.provide('cauliflowervest.LogsPage');


/**
 * Page responsible for displaying all types of logs.
 */
cauliflowervest.LogsPage = Polymer({
  is: 'cv-logs-page',
  properties: {
    state: {
      type: String,
      notify: true,
      observer: 'parseState_'
    },
    title: {
      type: String,
      readOnly: true,
      value: 'Access Logs',
    },
    route_: {
      type: String,
      observer: 'updateState_',
      value: 'created'
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
  },

  /**
   * @param {string} state
   */
  parseState_: function(state) {
    var prefix = 'log/';
    if (state.substr(0, prefix.length) != prefix) {
      this.updateState_();
      return;
    }
    state = state.substr(prefix.length);

    var values = ['created', 'bitlocker', 'filevault', 'luks', 'provisioning'];
    for (var i = 0; i < values.length; i++) {
      var t = values[i] + '/';
      if (state.substr(0, t.length) == t) {
        this.route_ = values[i];
        this[values[i] + 'State_'] = state;
        break;
      }
    }
  },

  updateState_: function() {
    // filter uninitilized components
    var substate = this[this.route_ + 'State_'];
    if (!goog.isString(substate) || substate.length == 0) {
      return;
    }

    this.state = 'log/' + substate;
  },
});
