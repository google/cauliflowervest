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
      observer: 'requestResults_',
    },

    field: {
      type: String,
      observer: 'requestResults_',
    },

    value: {
      type: String,
      observer: 'requestResults_',
    },

    prefixSearch: {
      type: String,
      observer: 'requestResults_',
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
    let volume = {
      data: [],
      id: vol.id,
      uuid: vol.volume_uuid,
      inactive: !vol.active,
      timestamp: (new Date(vol.created)).getTime(),
    };
    for (let k = 0; k < FIELD_ORDER_.length; k++) {
      let field = FIELD_ORDER_[k];
      if (!(field in vol)) {
        continue;
      }
      let value = vol[field];
      if (field == 'created') {
        let date = new Date(value);
        value = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      }
      let description = {
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

  /** @param {!Event} event */
  onResponse_: function(event) {
    let data = /** @type {!Array<Volume_>} */(event.detail.response);
    let volumes = [];
    for (let i = 0; i < data.length; i++) {
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

    let importantFields = ['hostname', 'volume_uuid', 'owner', 'created'];
    if (importantFields.indexOf(key) != -1 || this.field == key) {
      return '';
    }

    return 'hidden';
  },

  /** @param {!Event} event */
  onNetworkError_: function(event) {
    this.fire(
        'iron-signal', {
          name: 'network-error',
          data: event.detail.request.status,
        });
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

  /** @param {!Event} event */
  changeOwner_: function(event) {
    /** @type {SearchOwnerEditIconDataSet_} */
    let data = event.target.dataset;
    let volumeId = data.id;
    let currentOwner = data.owner;

    /** @type {cauliflowervest.ChangeOwnerDialog} */
    let changeOwnerDialog = this.$.changeOwner;
    changeOwnerDialog.open(this.searchType, volumeId, currentOwner);
  },

  requestResults_: function() {
    if (this.searchType && this.field && this.value) {
      this.$.request.generateRequest();
    }
  },

  /** @param {!DomRepeatEvent_} e */
  onRetrieveButtonClick_: function(e) {
    let volume = e.model.volume;
    let url = '/ui/#/retrieve/' + this.searchType + '/' + volume.uuid +
        '/' + volume.id;
    window.location = url;
  },
});
});  // goog.scope
