goog.provide('cauliflowervest.App');

goog.require('cauliflowervest.LogsPage');
goog.require('cauliflowervest.RevealSecret');
goog.require('cauliflowervest.SearchPage');
goog.require('goog.events');
goog.require('goog.events.EventType');


/**
 * Root UI element.
 */
cauliflowervest.App = Polymer({
  is: 'cauliflowervest-app',
  properties: {
    state: {
      type: String,
      notify: true,
      observer: 'parseState_',
    },
    adminState_: {
      type: String,
      value: 'admin/',
    },
    logState_: {
      type: String,
      observer: 'updateState_',
    },
    searchState_: {
      type: String,
      observer: 'updateState_',
    },
    retrieveState_: {
      type: String,
      observer: 'updateState_',
    },
    mainMenuSelection_: {
      type: String,
      value: 'search',
      observer: 'updateState_',
    },
    remoteUnlockState_: {
      type: String,
      value: 'remoteUnlock/',
    },
    title: {
      type: String,
    },
  },

  initialized_: false,

  /** @override */
  ready: function() {
    // TODO(user): use iron-location, after API will be stabilized
    goog.events.listen(window, goog.events.EventType.HASHCHANGE, (function() {
      this.state = location.hash;
    }).bind(this));
    this.state = location.hash;

    this.initialized_ = true;
  },

  updateState_: function() {
    var substate = '';

    if (this[this.mainMenuSelection_ + 'State_']) {
      substate = this[this.mainMenuSelection_ + 'State_'];
    }

    this.state = '#/' + substate;

    if (this.initialized_) {
      location.hash = this.state;
    }
  },


  /** @param {string} state */
  parseState_: function(state) {
    var values = ['search', 'log', 'retrieve', 'admin', 'remoteUnlock'];
    for (var i = 0; i < values.length; i++) {
      var t = '#/' + values[i] + '/';
      if (state.substr(0, t.length) == t) {
        this[values[i] + 'State_'] = state.substr(2);
        this.mainMenuSelection_ = values[i];
        break;
      }
    }

    // wait until lazy-page initialized
    setTimeout(this.updateTitle_.bind(this), 20);
  },

  updateTitle_: function() {
    var page =
        /** @type {
            cauliflowervest.LogsPage|
            cauliflowervest.RevealSecret|
            cauliflowervest.SearchPage} */
        (this.$$('#' + this.mainMenuSelection_));
    if (goog.isDefAndNotNull(page)) {
      this.title = page.title;
    } else {
      setTimeout(this.updateTitle_.bind(this), 20);
    }
  },

  openDrawer_: function() {
    this.$.drawerPanel.openDrawer();
  },

  closeDrawer_: function() {
    this.$.drawerPanel.closeDrawer();
  },

  resetSubstate_: function() {
    this.logState_ = 'log/';
    this.searchState_ = 'search/';
  },

  handleSchemaUpdate_: function() {
  },

  /** @param {!Event} e */
  handleNetworkError_: function(e) {
    if (e.detail == 403) {
      this.$.accessDeniedDialog.open();
    } else {
      this.$.networkErrorDialog.open();
    }
  }
});
