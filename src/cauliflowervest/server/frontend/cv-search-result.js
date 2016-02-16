goog.provide('cauliflowervest.SearchResult');

goog.require('cauliflowervest.ChangeOwnerDialog');


/**
 * dataset on "change owner" buttons.
 * @typedef {{
 *    uuid: string,
 *    owner: string,
 * }}
 */
var SearchOwnerEditIconDataSet_;


/**
 * Server response to /search.
 * @typedef {{
 *    volumes: Array<{data: !Array, uuid: string}>,
 * }}
 */
var SearchResultServerResponse_;


/**
 * Event for item inside dom-repeat.
 * @typedef {{
 *    model: Object,
 * }}
 */
var DomRepeatEvent_;


/**
 * Table with search results for query(searchType/field/value/prefixSearch).
 */
cauliflowervest.SearchResult = Polymer({
  is: 'cv-search-result',
  properties: {
    searchType: {
      type: String,
      observer: 'update_',
    },
    field: {
      type: String,
      observer: 'update_',
    },
    value: {
      type: String,
      observer: 'update_',
    },
    prefixSearch: {
      type: String,
      observer: 'update_',
    },
    loading_: {
      type: Boolean,
      value: true,
    },
    showAll_: {
      type: Boolean,
      value: false,
    },
    volumes_: {
      type: Array,
      value: function() {
        return [];
      }
    },
    fields_: {
      type: Array,
      value: function() {
        return [];
      }
    },
  },

  /** @param {!Event} e */
  handleResponse_: function(e) {
    /** @type {SearchResultServerResponse_} */
    var data = e.detail.response;
    var volumes = data.volumes;

    this.fields_ = [];
    if (volumes.length) {
      this.fields_ = volumes[0].data;
    }

    this.volumes_ = volumes;
  },

  cssClassForCell_: function(key, showAll) {
    if (showAll) {
      return '';
    }

    var importantFields = ['hostname', 'volume_uuid', 'owner', 'created'];
    if (importantFields.indexOf(key) != -1 || this.field == key) {
      return '';
    }

    return 'hidden';
  },

  /** @param {!Event} e */
  handleNetworkError_: function(e) {
    this.fire(
        'iron-signal', {name: 'network-error', data: e.detail.request.status});
  },

  /** @param {!Event} e */
  changeOwner_: function(e) {
    /** @type {SearchOwnerEditIconDataSet_} */
    var data = e.target.dataset;
    var volumeUuid = data.uuid;
    var currentOwner = data.owner;

    /** @type {cauliflowervest.ChangeOwnerDialog} */
    var changeOwnerDialog = this.$.changeOwner;
    changeOwnerDialog.open(this.searchType, volumeUuid, currentOwner);
  },

  update_: function() {
    if (this.searchType && this.field && this.value) {
      this.$.request.generateRequest();
    }
  },

  /** @param {!DomRepeatEvent_} e */
  handleRetrieveButtonClick_: function(e) {
    var volume = e.model.volume;
    var url = '/ui/#/retrieve/' + this.searchType + '/' + volume.uuid;
    window.location = url;
  },
});
