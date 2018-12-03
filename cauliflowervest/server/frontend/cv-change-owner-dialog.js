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
 * @final
 * @polymer
 */
class CvChangeOwnerDialog extends Polymer.Element {
  constructor() {
    super();

    /** @private {string} */
    this.volumeUuid_;
    /** @private {string} */
    this.volumeId_;
    /** @private {string} */
    this.currentOwner_;
    /** @private {string} */
    this.volumeType;
    /** @private {string} */
    this.xsrfToken_;
    /** @private {string} */
    this.newOwner_;
  }

  /**
   * @return {string} element identifier.
   */
  static get is() {
    return 'cv-change-owner-dialog';
  }

  /**
   * The properties of the Polymer element.
   * @return {!PolymerElementProperties}
   */
  static get properties() {
    return {
      volumeUuid_: String,
      volumeId_: String,
      currentOwner_: String,
      volumeType_: String,
      xsrfToken_: String,
      newOwner_: String,
    };
  }

  /**
   * Open dialog.
   * @param {string} volumeType
   * @param {string} volumeUuid
   * @param {string} volumeId
   * @param {string} currentOwner
   */
  open(volumeType, volumeUuid, volumeId, currentOwner) {
    this.volumeType_ = volumeType;
    this.volumeUuid_ = volumeUuid;
    this.volumeId_ = volumeId;
    this.currentOwner_ = currentOwner;
    this.newOwner_ = currentOwner;

    this.$.dialog.open();
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
   * @param {!Event} event
   * @private
   */
  submitForm_(event) {
    this.xsrfToken_ = event.detail.response;

    this.$.form.submit();
  }

  /** @private */
  requestToken_() {
    if (this.newOwner_ == this.currentOwner_) {
      this.$.dialog.close();
      return;
    }
    this.$.tokenRequest.generateRequest();
  }

  /** @private */
  onIronFormResponse_() {
    this.dispatchEvent(new CustomEvent('cv-owner-changed'));
    this.$.dialog.close();
  }
}

customElements.define(CvChangeOwnerDialog.is, CvChangeOwnerDialog);
