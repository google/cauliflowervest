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
 * Page responsible for displaying single escrow result.
 * @polymer
 */
class CvRevealSecret extends Polymer.Element {
  /**
   * @return {string} element identifier.
   */
  static get is() {
    return 'cv-reveal-secret';
  }

  /**
   * The properties of the Polymer element.
   * @return {!Object}
   */
  static get properties() {
    return {
      searchType: String,

      volumeUuid: String,

      volumeId: String,

      state: {
        type: String,
        observer: 'stateChanged_',
      },

      title: {
        type: String,
        value: 'Escrow Result',
        readOnly: true,
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

      tag_: String,

      data_: {
        type: Object,
        value: function() {
          return {escrow_secret: ''};
        },
        notify: true,
      },
    };
  }

  /** @override */
  static get observers() {
    return [
      'onSecretChanged_(data_.escrow_secret)'
    ];
  }

  constructor() {
    super();

    /** @private {?SpeechSynthesisUtterance} */
    this.spellInProgress_ = null;
  }

  /**
   * @param {string} symbol
   * @return {string}
   */
  static symbolToText(symbol) {
    if (symbol.toUpperCase() != symbol) {
      return 'lower case ' + symbol;
    }
    if (symbol == '-') {
      return 'dash';
    }
    return symbol;
  }

  /**
   * Display new secret.
   * @private
   */
  onSecretChanged_() {
    this.set('secret_', this.data_.escrow_secret);
    this.set('rest_', '');
    this.set('selectedLetter_', '');
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
  onTokenResponse_(event) {
    this.xsrfToken_ = event.detail.response;

    this.$.dataRequest.generateRequest();
  }

  /**
   * @param {string} s
   * @return {string}
   * @private
   */
  encode_(s) {
    return encodeURIComponent(s);
  }

  /** @private */
  showPasswordTooltip_() {
    this.$.passwordTooltip.show();
  }

  /**
   * Parse state previosly saved as last part of uri.
   * example state:  bitlocker/volume_uuid/optional-id/optional-tag
   * @param {string} newValue
   * @private
   */
  stateChanged_(newValue) {
    let state = newValue.substr(1).split('/');

    if (state.length < 2 || state.length > 4) {
      return;
    }

    this.searchType = state[0];
    this.volumeUuid = state[1];

    // if tag_ is non-default ignoring volumeId.
    this.tag_ = (state.length == 4) ? state[3] : 'default';
    this.volumeId = (state.length == 3) ? state[2] : '';

    this.$.tokenRequest.generateRequest();
  }

  /**
   * Spell word. highlight letter during spelling.
   * @param {string} text
   * @param {number=} i
   * @private
   */
  spellWord_(text, i = 0) {
    if (i >= text.length) {
      this.spellInProgress_ = null;
      this.onSecretChanged_();
      return;
    }

    this.set('secret_', text.substr(0, i));
    this.set('selectedLetter_', text[i]);
    this.set('rest_', text.substr(i + 1));

    const msg = new SpeechSynthesisUtterance(CvRevealSecret.symbolToText(text[i]));
    msg.rate = 0.5;
    msg.onend = () => {
      this.spellWord_(text, i + 1);
    };
    window.speechSynthesis.speak(msg);

    this.spellInProgress_ = msg;
  }

  /** @private */
  textToSpeach_() {
    if (this.spellInProgress_) {
      return;
    }
    this.spellWord_(this.data_.escrow_secret);
  }
}

customElements.define(CvRevealSecret.is, CvRevealSecret);
