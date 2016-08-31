goog.provide('cauliflowervest.AdminPage');


/** Various maintenance actions. */
cauliflowervest.AdminPage = Polymer({
  is: 'cv-admin-page',
  properties: {
    state: {
      type: String,
      value: '/admin/',
    },
    xsrfToken_: String,
  },

  /** @param {!Event} e */
  handleToken_: function(e) {
    this.xsrfToken_ = e.detail.response;

    this.$.dataRequest.generateRequest();
  },

  handleSchemaUpdate_: function() {
    this.$.tokenRequest.generateRequest();
  },

  /** @param {!Event} e */
  handleNetworkError_: function(e) {
    this.fire(
        'iron-signal', {name: 'network-error', data: e.detail.request.status});
  },
});
