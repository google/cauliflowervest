goog.provide('cauliflowervest.ChangeOwnerDialog');


/**
 * Pop-up dialog to change volume's owner.
 */
cauliflowervest.ChangeOwnerDialog = Polymer({
  is: 'cv-change-owner-dialog',
  properties: {
    volumeId: String,
    currentOwner: String,
    volumeType: String,
    xsrfToken: String,
    newOwner: String,
  },

  /**
   * Open dialog.
   * @param {string} volumeType
   * @param {string} volumeId
   * @param {string} currentOwner
   */
  open: function(volumeType, volumeId, currentOwner) {
    this.volumeType = volumeType;
    this.volumeId = volumeId;
    this.currentOwner = currentOwner;
    this.newOwner = currentOwner;

    this.$.dialog.open();
  },

  /** @param {!Event} e */
  handleNetworkError_: function(e) {
    this.fire(
        'iron-signal', {name: 'network-error', data: e.detail.request.status});
  },

  /** @param {!Event} e */
  submitForm_: function(e) {
    this.xsrfToken = e.detail.response;

    this.$.form.submit();
  },

  requestToken_: function() {
    if (this.newOwner == this.currentOwner) {
      this.$.dialog.close();
      return;
    }
    this.$.tokenRequest.generateRequest();
  },

  /** @param {!Event} e */
  handleFormResponse_: function(e) {
    this.fire('owner-changed');
    this.$.dialog.close();
  }
});
