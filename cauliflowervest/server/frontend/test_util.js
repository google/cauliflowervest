//
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
//
//
goog.setTestOnly();

goog.provide('cauliflowervest.test');
goog.require('goog.Timer');
goog.require('goog.testing.MockControl');
goog.require('goog.testing.TestCase');


/**
 * wait for dom update.
 * @param {number=} opt_delay
 * @return {goog.Timer.promise}
 */
cauliflowervest.test.wait = function(opt_delay) {
  let delay = 100;
  if (opt_delay) {
    delay = opt_delay;
  }

  Polymer.dom.flush();
  return goog.Timer.promise(delay);
};


/**
 * Respond with prefixed json to sinon request.
 * @param {!Object} request
 * @param {!Object} obj
 */
cauliflowervest.test.respondToRequest = function(request, obj) {
  let JSON_PREFIX = ')]}\',\n';

  request.respond(
      200, { 'Content-Type': 'application/json' },
      JSON_PREFIX + JSON.stringify(obj));
};


/**
 * Global variables for test case. Managed by createSetUpForComponent/tearDown.
 */
cauliflowervest.test.state = {};


/**
 * Create setUp function for component.
 * @param {string} name
 * @return {function}
 */
cauliflowervest.test.createSetUpForComponent = function(name) {
  return function() {
    goog.testing.TestCase.getActiveTestCase().promiseTimeout = 15000;

    cauliflowervest.test.state.server = sinon.fakeServer.create();
    cauliflowervest.test.state.mockControl = new goog.testing.MockControl();
    cauliflowervest.test.state.signals = document.createElement('iron-signals');
    cauliflowervest.test.state.component = document.createElement(name);

    document.body.appendChild(cauliflowervest.test.state.component);
    document.body.appendChild(cauliflowervest.test.state.signals);
  }
};


/**
 * pair for setUp function created by createSetUpForComponent.
 */
cauliflowervest.test.tearDown = function() {
  cauliflowervest.test.state.server.restore();
  cauliflowervest.test.state.mockControl.$resetAll();

  document.body.removeChild(cauliflowervest.test.state.component);
  document.body.removeChild(cauliflowervest.test.state.signals);

  cauliflowervest.test.state.component = undefined;
  cauliflowervest.test.state.signals = undefined;
  cauliflowervest.test.state.mockControl = undefined;
  cauliflowervest.test.state.server = undefined;
};
