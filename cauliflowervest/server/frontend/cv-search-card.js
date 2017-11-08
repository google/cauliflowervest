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

var DISABLED_PREFIX_SEARCH_ = ['created_by', 'asset_tags'];


/**
 * Search form for single volume type.
 */
Polymer({
  is: 'cv-search-card',
  properties: {
    title: String,

    type: String,

    value1: String,

    fields: {
      type: Array,
      value: function() {
        return [];
      }
    },
    prefixSearch_: Boolean,
  },

  attached: function() {
    if (this.type == 'bitlocker') {
      this.prefixSearch_ = true;
    }
  },

  onItemSelect_: function() {
    let field = this.fields[this.$.menu.selected][0];
    if (this.$.menu.selectedItem &&
        DISABLED_PREFIX_SEARCH_.indexOf(field) != -1) {
      this.$.checkbox.disabled = true;
      this.prefixSearch_ = false;
    } else {
      this.$.checkbox.disabled = false;
    }
  },

  search_: function() {
    let params = {
      searchType: this.type,
      field: this.fields[this.$.menu.selected][0],
      value: encodeURIComponent(this.value1),
      prefixSearch: '',
    };
    if (this.prefixSearch_) {
      params.prefixSearch = '1';
    }

    this.fire('search', params);
  },
});
