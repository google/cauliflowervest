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
 * Root UI element.
 */
Polymer({
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
      let page = this.$$('#' + this.data_.mainMenuSelection);
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
    if (event.detail.data == 403) {
      this.$.accessDeniedDialog.open();
    } else {
      this.$.networkErrorDialog.open();
    }
  }
});
