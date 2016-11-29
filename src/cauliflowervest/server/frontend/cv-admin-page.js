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

  /** @param {!Event} event */
  onResponse_: function(event) {
    this.xsrfToken_ = event.detail.response;

    this.$.dataRequest.generateRequest();
  },

  onClick_: function() {
    this.$.tokenRequest.generateRequest();
  },

  /** @param {!Event} event */
  onNetworkError_: function(event) {
    this.fire(
        'iron-signal', {
          name: 'network-error',
          data: event.detail.request.status
        });
  },
});
