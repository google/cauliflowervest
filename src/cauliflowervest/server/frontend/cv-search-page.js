goog.provide('cauliflowervest.SearchPage');


/**
 * Fields detail for volume type.
 * @typedef {{
 *    type: string,
 *    name: string,
 *    fields: Array,
 *    retrieve_own: boolean,
 * }}
 */
var VolumeType_;


/**
 * Information detail about all volume types.
 * @typedef {{
 *    bitlocker: VolumeType_,
 *    filevault: VolumeType_,
 *    luks: VolumeType_,
 *    provisioning: VolumeType_,
 *    user: !string,
 * }}
 */
var SearchPageServerResponse_;


/**
 *  User facing strings.
 */
cauliflowervest.HUMAN_READABLE_VOLUME_TYPE = {
  bitlocker: 'BitLocker (Windows)',
  filevault: 'FileVault (Mac OS X)',
  luks: 'LUKS (Linux)',
  provisioning: 'Provisioning',
};


/**
 * Page responsible for displaying search results and search forms.
 */
cauliflowervest.SearchPage = Polymer({
  is: 'cv-search-page',
  properties: {
    state: {
      type: String,
      notify: true,
      observer: 'parseState_',
    },
    title: {
      type: String,
      readOnly: true,
      value: 'Escrow Search',
    },
    loading_: {
      type: Boolean,
      value: false,
    },
    volumeTypes_: {
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
    user_: String,
  },

  /** @param {!Event} e */
  handleNetworkError_: function(e) {
    this.fire(
        'iron-signal', {name: 'network-error', data: e.detail.request.status});
  },

  /** @param {!Event} e */
  handleResponse_: function(e) {
    let data = /** @type {SearchPageServerResponse_} */(e.detail.response);

    let types = [];
    for (let type in cauliflowervest.HUMAN_READABLE_VOLUME_TYPE) {
      if (type in data) {
        data[type].type = type;
        data[type].name = cauliflowervest.HUMAN_READABLE_VOLUME_TYPE[type];
        types.push(data[type]);
      }
    }
    this.volumeTypes_ = types;

    this.user_ = data.user;
  },

  check_: function(e) {
    return Boolean(e);
  },

  /** @param {string} state */
  parseState_: function(state) {
    try {
      let params = state.substr(1).split('/');
      this.searchType_ = params[0];
      this.field_ = params[1];
      this.value_ = params[2];
      this.prefixSearch_ = params[3];
    } catch (e) {
      this.searchType_ = '';
    }
  },

  updateState_: function() {
    this.state = '/' + this.searchType_ + '/' + this.field_ +
        '/' + this.value_ + '/' + this.prefixSearch_;
  },

  /** @param {!Event} e */
  handleSearch_: function(e) {
    this.searchType_ = e.detail.searchType;
    this.field_ = e.detail.field;
    this.value_ = e.detail.value;
    this.prefixSearch_ = e.detail.prefixSearch;

    this.updateState_();
  },

  /** @param {!Array<VolumeType_>} volumeTypes */
  canRetrieveOwn_: function(volumeTypes) {
    for (let i = 0; i < volumeTypes.length; i++) {
      if (volumeTypes[i].retrieve_own) {
        return true;
      }
    }
    return false;
  },

  handleSearchOwnVolumes_: function() {
    let n = this.$$('#ownVolumesMenu').selected;
    let type;
    for (let i = 0, k = 0; i < this.volumeTypes_.length; i++) {
      if (!this.volumeTypes_[i]['retrieve_own']) {
        continue;
      }
      if (k == n) {
        type = this.volumeTypes_[i].type;
        break;
      }
      k++;
    }
    this.searchType_ = type;
    this.field_ = 'owner';
    this.value_ = this.user_;
    this.prefixSearch_ = '0';

    this.updateState_();
  }
});
