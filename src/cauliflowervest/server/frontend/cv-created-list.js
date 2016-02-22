goog.provide('cauliflowervest.CreatedList');


/**
 * List of volumes created by current user.
 */
cauliflowervest.CreatedList = Polymer({
  is: 'cv-created-list',
  properties: {
    loading_: {
      type: Boolean,
      value: true,
    },
    volumes_: {
      type: Array,
      notify: true,
      value: function() {
        return [];
      }
    }
  },

  /** @param {!Event} e */
  handleNetworkError_: function(e) {
    this.fire(
        'iron-signal', {name: 'network-error', data: e.detail.request.status});
  },

  /** @param {!Event} e */
  handleResponse_: function(e) {
    this.volumes_ = /** @type {!Array} */(e.detail.response);
  },
});
