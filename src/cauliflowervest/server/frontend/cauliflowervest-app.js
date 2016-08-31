goog.provide('cauliflowervest.App');

goog.require('cauliflowervest.LogsPage');
goog.require('cauliflowervest.RevealSecret');
goog.require('cauliflowervest.SearchPage');


/**
 * Root UI element.
 */
cauliflowervest.App = Polymer({
  is: 'cauliflowervest-app',
  properties: {
    route_: {
      type: Object,
      value: function() {
        return {path: '/'};
      },
    },
    tail_: {
      type: Object,
      value: function() {
        return {};
      },
    },
    data_: {
      type: Object,
      value: function() {
        return {
          mainMenuSelection: 'search',
        };
      },
    },
    title: {
      type: String,
    },
  },
  observers: [
    'handleStateChange_(route_.path)'
  ],

  /** @param {string} state */
  handleStateChange_: function(state) {
    if (!this.route_.path) {
      this.set('route_.path', '/search');
    }
    // wait until lazy-page initialized
    setTimeout(this.updateTitle_.bind(this), 20);
  },

  updateTitle_: function() {
    if (this.data_.mainMenuSelection) {
      var page =
          /** @type {
              cauliflowervest.LogsPage|
              cauliflowervest.RevealSecret|
              cauliflowervest.SearchPage} */
          (this.$$('#' + this.data_.mainMenuSelection));
      if (goog.isDefAndNotNull(page)) {
        this.title = page.title;
        return;
      }
    }
    setTimeout(this.updateTitle_.bind(this), 20);
  },

  openDrawer_: function() {
    this.$.drawerPanel.openDrawer();
  },

  closeDrawer_: function() {
    this.$.drawerPanel.closeDrawer();
  },

  resetSubstate_: function() {
    this.tail_.path = '';
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
