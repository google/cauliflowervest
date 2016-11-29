goog.provide('cauliflowervest.RevealSecret');


/**
 * Page responsible for displaying single escrow result.
 */
cauliflowervest.RevealSecret = Polymer({
  is: 'cv-reveal-secret',
  properties: {
    searchType: String,

    volumeUuid: String,

    volumeId: String,

    state: {
      type: String,
      observer: 'stateChanged_',
    },

    title: {
      type: String,
      readOnly: true,
      value: 'Escrow Result'
    },

    xsrfToken_: String,

    selected_: {
      type: Number,
      value: 0
    },

    loading_: {
      type: Boolean,
      value: true
    },

    data_: {
      type: Object,
      value: function() {
        return {};
      }
    },
  },

  /** @param {!Event} event */
  onNetworkError_: function(event) {
    this.fire(
        'iron-signal', {
          name: 'network-error',
          data: event.detail.request.status
        });
  },

  /** @param {!Event} event */
  onTokenResponse_: function(event) {
    this.xsrfToken_ = event.detail.response;

    this.$.dataRequest.generateRequest();
  },

  /** @param {string} s */
  encode_: function(s) {
    return encodeURIComponent(s);
  },

  showPasswordTooltip_: function() {
    this.$$('#password-tooltip').show();
  },

  /**
   * Parse state previosly saved as last part of uri.
   * example state:  bitlocker/foo-uuid/optional-id
   * @param {string} newValue
   */
  stateChanged_: function(newValue) {
    let state = newValue.substr(1).split('/');

    if (state.length < 2 || state.length > 3) {
      return;
    }

    this.searchType = state[0];
    this.volumeUuid = state[1];
    this.volumeId = (state.length == 3) ? state[2] : '';

    this.$.tokenRequest.generateRequest();
  }
});
