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
    route_: Object,

    searchState_: Object,
    retrieveState_: Object,
    logState_: Object,

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
    'onPathChanged_(route_.path)'
  ],

  onPathChanged_: function() {
    if (!this.route_.path) {
      this.set('route_.path', '/search');
    }
    // wait until lazy-page initialized
    setTimeout(() => this.updateTitle_(), 20);
  },

  updateTitle_: function() {
    if (this.data_.mainMenuSelection) {
      let page =
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
    setTimeout(() => this.updateTitle_(), 20);
  },

  openDrawer_: function() {
    this.$.drawerPanel.openDrawer();
  },

  closeDrawer_: function() {
    this.$.drawerPanel.closeDrawer();
  },

  resetSubstate_: function() {
    this.set('searchState_.path', '');
    this.set('logState_.path', '');
    this.set('retrieveState_.path', '');
  },

  /** @param {!Event} event */
  onNetworkError_: function(event) {
    if (event.detail == 403) {
      this.$.accessDeniedDialog.open();
    } else {
      this.$.networkErrorDialog.open();
    }
  }
});
