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
 * Pop-up dialog to change volume's owner.
 */
Polymer({
  is: 'cv-change-owner-dialog',
  properties: {
    volumeUuid: String,

    volumeId: String,

    currentOwner: String,

    volumeType: String,

    xsrfToken: String,

    newOwner: String,
  },

  /**
   * Open dialog.
   * @param {string} volumeType
   * @param {string} volumeUuid
   * @param {string} volumeId
   * @param {string} currentOwner
   */
  open: function(volumeType, volumeUuid, volumeId, currentOwner) {
    this.volumeType = volumeType;
    this.volumeUuid = volumeUuid;
    this.volumeId = volumeId;
    this.currentOwner = currentOwner;
    this.newOwner = currentOwner;

    this.$.dialog.open();
  },

  /** @param {!Event} event */
  onNetworkError_: function(event) {
    this.fire('cv-network-error', {data: event.detail.request.status});
  },

  /** @param {!Event} event */
  submitForm_: function(event) {
    this.xsrfToken = event.detail.response;

    this.$.form.submit();
  },

  requestToken_: function() {
    if (this.newOwner == this.currentOwner) {
      this.$.dialog.close();
      return;
    }
    this.$.tokenRequest.generateRequest();
  },

  onIronFormResponse_: function() {
    this.fire('owner-changed');
    this.$.dialog.close();
  }
});
