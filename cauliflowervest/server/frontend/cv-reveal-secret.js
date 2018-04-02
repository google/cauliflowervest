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
 */
Polymer({
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
      notify: true,
      value: function() {
        return {escrow_secret: ''};
      }
    },
  },

  observers: [
    'onSecretChanged_(data_.escrow_secret)'
  ],

  /** Display new secret. */
  onSecretChanged_: function() {
    this.set('secret_', this.data_.escrow_secret);
    this.set('rest_', '');
    this.set('selectedLetter_', '');
  },

  /** @param {!Event} event */
  onNetworkError_: function(event) {
    this.fire('cv-network-error', {data: event.detail.request.status});
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
  },

  /**
   * Spell word. highlight letter during spelling.
   * @param {string} text
   * @param {number=} i
   */
  spellWord_: function(text, i = 0) {
    if (i >= text.length) {
      this.spellInProgress_ = null;
      this.onSecretChanged_();
      return;
    }

    this.set('secret_', text.substr(0, i));
    this.set('selectedLetter_', text[i]);
    this.set('rest_', text.substr(i + 1));
    let letter = text[i];
    if (letter == '-') {
      letter = 'dash';
    }
    const msg = new SpeechSynthesisUtterance(letter);
    msg.rate = 0.7;
    msg.onend = () => {
      this.spellWord_(text, i + 1);
    };
    window.speechSynthesis.speak(msg);

    this.spellInProgress_ = msg;
  },

  textToSpeach_: function() {
    if (this.spellInProgress_) {
      return;
    }
    this.spellWord_(this.data_.escrow_secret);
  },
});
