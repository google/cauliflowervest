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

  /** @param {!Event} event */
  onNetworkError_: function(event) {
    this.fire(
        'iron-signal', {
          name: 'network-error',
          data: event.detail.request.status
        });
  },
});
