goog.provide('cauliflowervest.SearchCard');


/**
 * Search form for single volume type.
 */
cauliflowervest.SearchCard = Polymer({
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
  },

  handleItemSelect_: function() {
    if (this.$.menu.selectedItem &&
        this.fields[this.$.menu.selected][0] == 'created_by') {
      this.$.checkbox.style.display = 'none';
      this.$.checkbox.checked = false;
    } else {
      this.$.checkbox.style.display = 'inline-block';
    }
  },

  handleSearch_: function() {
    var params = {
      searchType: this.type,
      field: this.fields[this.$.menu.selected][0],
      value: encodeURIComponent(this.value1),
      prefixSearch: '',
    };
    if (this.$.checkbox.checked) {
      params.prefixSearch = '1';
    }

    this.fire('search', params);
  },
});
