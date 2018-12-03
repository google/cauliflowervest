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
 * dataset on "change owner" buttons.
 * @typedef {{
 *    uuid: string,
 *    owner: string,
 * }}
 */
let SearchOwnerEditIconDataSet_;


/**
 * Event for item inside dom-repeat.
 * @typedef {{
 *    model: Object,
 * }}
 */
let DomRepeatEvent_;


/**
 * Server response to /search.
 * @typedef {{
 *    volume_uuid: String,
 *    target_id: string,
 *    hostname: String,
 *    platform_uuid: String,
 *    owners: Array,
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
let Volume_;


const HUMAN_READABLE_VOLUME_FIELD_NAME_ = {
  volume_uuid: 'Volume UUID',
  hostname: 'Hostname',
  platform_uuid: 'Platform UUID',
  owners: 'Owners',
  created_by: 'Creator',
  serial: 'Serial',
  hdd_serial: 'Hard Disk Serial',
  dn: 'DN',
  when_created: 'When Created',
  created: 'Creation time (UTC)',
  asset_tags: 'Asset Tag',
};


const FIELD_ORDER_ = [
  'volume_uuid', 'hostname', 'platform_uuid', 'owners', 'created_by', 'serial',
  'hdd_serial', 'dn', 'when_created', 'asset_tags', 'created',
];

const IMPORTANT_FIELDS_ = [
  'hostname', 'volume_uuid', 'owners', 'created', 'asset_tags'
];


/**
 * Table with search results for query(searchType/field/value/prefixSearch).
 * @polymer
 */
class CvSearchResult extends Polymer.Element {
  /**
   * @return {string} element identifier.
   */
  static get is() {
    return 'cv-search-result';
  }

  /**
   * The properties of the Polymer element.
   * @return {!Object}
   */
  static get properties() {
    return {
      searchType: String,

      field: String,

      value: String,

      prefixSearch: String,

      loading_: {
        type: Boolean,
        value: true,
      },

      showAll_: {
        type: Boolean,
        value: false,
      },

      tooManyResults_: {
        type: Boolean,
        value: false,
      },

      resultsAccessWarning_: {
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
    };
  }

  /** @override */
  static get observers() {
    return [
      'requestResults_(searchType, field, value, prefixSearch)',
    ];
  }

  /**
    * @param {!Volume_} vol
    * @return {Object}
    * @private
    */
  prepareVolumeForTemplate_(vol) {
    let volume = {
      data: [],
      id: vol.id,
      uuid: vol.target_id,
      inactive: !vol.active,
      timestamp: (new Date(vol.created)).getTime(),
    };
    for (let k = 0; k < FIELD_ORDER_.length; k++) {
      let field = FIELD_ORDER_[k];
      if (!(field in vol)) {
        continue;
      }
      let value = vol[field];
      if (field == 'created' || field == 'when_created') {
        let date = new Date(value);
        value = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
      }
      let description = {
        key: field,
        name: HUMAN_READABLE_VOLUME_FIELD_NAME_[field],
        value: value,
      };
      if (field == 'owners' && 'change_owner_link' in vol) {
        description.edit_link = vol.change_owner_link;

        description.value = description.value.join(', ');
      }
      volume.data.push(description);
    }

    return volume;
  }

  /**
    * @param {!Event} event
    * @private
    */
  onResponse_(event) {
    let response = /** @type {!Object} */(event.detail.response);
    let data = response['passphrases'];
    let volumes = [];

    this.resultsAccessWarning_ = response['results_access_warning'];
    this.tooManyResults_ = response['too_many_results'];
    for (let volume of data) {
      volumes.push(this.prepareVolumeForTemplate_(volume));
    }

    this.fields_ = [];
    if (volumes.length) {
      this.fields_ = volumes[0].data;
    }

    this.volumes_ = volumes;
  }

  /**
   * @param {string} key
   * @param {boolean} showAll
   * @return {string}
   * @private
   */
  cssClassForCell_(key, showAll) {
    if (showAll) {
      return '';
    }

    if (IMPORTANT_FIELDS_.indexOf(key) != -1 || this.field == key) {
      return '';
    }

    return 'hidden';
  }

  /**
   * @param {!Event} event
   * @private
   */
  onNetworkError_(event) {
    this.dispatchEvent(new CustomEvent(
        'cv-network-error', {
          detail: {data: event.detail.request.status},
          bubbles: true,
          composed: true,
       }));
  }

  /**
   * @param {!Boolean} inactive
   * @param {!Boolean} showInactive
   * @return {string}
   * @private
   */
  cssClassForVolume_(inactive, showInactive) {
    if (inactive) {
      if (showInactive) {
        return 'grey';
      }
      return 'hidden';
    }
    return '';
  }

  /**
   * @param {!Event} event
   * @private
   */
  changeOwner_(event) {
    /** @type {SearchOwnerEditIconDataSet_} */
    let data = event.target.dataset;
    let volumeId = data.id;
    let currentOwner = data.owner;
    let volume = event.model.volume;
    let volumeUuid = volume.uuid;

    let changeOwnerDialog = this.$.changeOwner;
    changeOwnerDialog.open(this.searchType, volumeUuid, volumeId, currentOwner);
  }

  /** @private */
  requestResults_() {
    if (this.searchType && this.field && this.value) {
      this.$.request.generateRequest();
    }
  }

  /**
   * @param {!DomRepeatEvent_} e
   * @private
   */
  onRetrieveButtonClick_(e) {
    let volume = e.model.volume;
    let url = '/ui/#/retrieve/' + this.searchType + '/' + volume.uuid +
        '/' + volume.id;
    window.location = url;
  }
}

customElements.define(CvSearchResult.is, CvSearchResult);
