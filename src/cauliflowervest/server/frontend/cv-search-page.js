goog.provide('cauliflowervest.SearchPage');


/**
 * Fields detail for volume types.
 * @typedef {{
 *    bitlocker_fields: !Array<string>,
 *    filevault_fields: !Array<string>,
 *    luks_fields: !Array<string>,
 *    provisioning_fields: !Array<string>,
 * }}
 */
var SearchPageServerResponse_;


/**
 * Page responsible for displaying search results and search forms.
 */
cauliflowervest.SearchPage = Polymer({
  is: 'cv-search-page',
  properties: {
    bitlockerFields_: {
      type: Array,
      value: function() {
        return [];
      }
    },
    filevaultFields_: {
      type: Array,
      value: function() {
        return [];
      }
    },
    luksFields_: {
      type: Array,
      value: function() {
        return [];
      }
    },
    provisioningFields_: {
      type: Array,
      value: function() {
        return [];
      }
    },
    searchType_: {
      type: String,
      value: '',
    },
    field_: String,
    value_: String,
    prefixSearch_: String,
    state: {
      type: String,
      notify: true,
      observer: 'parseState_',
      value: 'search/',
    },
    title: {
      type: String,
      readOnly: true,
      value: 'Escrow Search',
    }
  },

  /** @param {!Event} e */
  handleNetworkError_: function(e) {
    this.fire(
        'iron-signal', {name: 'network-error', data: e.detail.request.status});
  },

  /** @param {!Event} e */
  handleResponse_: function(e) {
    /** @type {SearchPageServerResponse_} */
    var data = e.detail.response;

    this.bitlockerFields_ = data.bitlocker_fields;
    this.filevaultFields_ = data.filevault_fields;
    this.luksFields_ = data.luks_fields;
    this.provisioningFields_ = data.provisioning_fields;
  },

  check_: function(e) {
    return Boolean(e);
  },

  /** @param {string} state */
  parseState_: function(state) {
    var prefix = 'search/';
    if (state.substr(0, prefix.length) != prefix) {
      this.searchType_ = '';
      return;
    }
    state = state.substr(prefix.length);
    try {
      var params = state.split('/');
      this.searchType_ = params[0];
      this.field_ = params[1];
      this.value_ = params[2];
      this.prefixSearch_ = params[3];
    } catch (e) {
      this.searchType_ = '';
    }
  },

  updateState_: function() {
    this.state = 'search/' + this.searchType_ + '/' + this.field_ +
        '/' + this.value_ + '/' + this.prefixSearch_;
  },

  /** @param {!Event} e */
  handleSearch_: function(e) {
    this.searchType_ = e.detail.searchType;
    this.field_ = e.detail.field;
    this.value_ = e.detail.value;
    this.prefixSearch_ = e.detail.prefixSearch;

    this.updateState_();
  }
});
