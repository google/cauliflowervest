'use strict';

goog.provide('cauliflower');
goog.require('goog.events');

cauliflower.connectTabsToPages = function() {
  var pages = document.querySelector('iron-pages');
  var tabs = document.querySelector('paper-tabs');

  goog.events.listen(tabs, 'iron-select', function() {
    pages.selected = tabs.selected;
  });
};

goog.scope(function() {
cauliflower.connectTabsToPages();
});
