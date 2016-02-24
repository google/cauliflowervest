goog.provide('cauliflowervest.SearchResult');

goog.require('cauliflowervest.ChangeOwnerDialog');


goog.scope(function() {


/**
 * dataset on "change owner" buttons.
 * @typedef {{
 *    uuid: string,
 *    owner: string,
 * }}
 */
var SearchOwnerEditIconDataSet_;


/**
 * Event for item inside dom-repeat.
 * @typedef {{
 *    model: Object,
 * }}
 */
var DomRepeatEvent_;


/**
 * Server response to /search.
 * @typedef {{
 *    volume_uuid: String,
 *    hostname: String,
 *    platform_uuid: String,
 *    owner: String,
 *    created_by: String,
 *    serial: String,
 *    hdd_serial: String,
 *    dn: String,
 *    when_created: String,
 *    created: String,
 *    change_owner_link: String,
 *    active: !Boolean,
 *    id: !String,
 * }}
 */
var Volume_;


var HUMAN_READABLE_VOLUME_FIELD_NAME_ = {
  volume_uuid: 'Volume UUID',
  hostname: 'Hostname',
  platform_uuid: 'Platform UUID',
  owner: 'Owner',
  created_by: 'Creator',
  serial: 'Serial',
  hdd_serial: 'Hard Disk Serial',
  dn: 'DN',
  when_created: 'When Created',
  created: 'Creation time (UTC)',
};


var FIELD_ORDER_ = [
  'volume_uuid', 'hostname', 'platform_uuid', 'owner', 'created_by', 'serial',
  'hdd_serial', 'dn', 'when_created', 'created',
];


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
    showInactive_: {
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

  /** @param {!Volume_} vol */
  prepareVolumeForTemplate_: function(vol) {
    var volume = {
      data: [],
      id: vol.id,
      uuid: vol.volume_uuid,
      inactive: !vol.active,
      timestamp: (new Date(vol.created)).getTime(),
    };
    for (var k = 0; k < FIELD_ORDER_.length; k++) {
      var field = FIELD_ORDER_[k];
      if (!(field in vol)) {
        continue;
      }
      var value = vol[field];
      if (field == 'created') {
        var date = new Date(value);
        value = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      }
      var description = {
        key: field,
        name: HUMAN_READABLE_VOLUME_FIELD_NAME_[field],
        value: value,
      };
      if (field == 'owner' && 'change_owner_link' in vol) {
        description.edit_link = vol.change_owner_link;
      }
      volume.data.push(description);
    }

    return volume;
  },

  /** @param {!Event} e */
  handleResponse_: function(e) {
    var data = /** @type {!Array<Volume_>} */(e.detail.response);
    var volumes = [];
    for (var i = 0; i < data.length; i++) {
      volumes.push(this.prepareVolumeForTemplate_(data[i]));
    }

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

  /**
   * @param {!Boolean} inactive
   * @param {!Boolean} showInactive
   */
  cssClassForVolume_: function(inactive, showInactive) {
    if (inactive) {
      if (showInactive) {
        return 'grey';
      }
      return 'hidden';
    }
    return '';
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
    var url = '/ui/#/retrieve/' + this.searchType + '/' + volume.uuid +
        '/' + volume.id;
    window.location = url;
  },
});
});  // goog.scope
