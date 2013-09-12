#!/usr/bin/python
#-*- coding: utf-8 -*-

###########################################################
# © 2011 Daniel 'grindhold' Brendle and Team
#
# This file is part of Skarphed.
#
# Skarphed is free software: you can redistribute it and/or 
# modify it under the terms of the GNU Affero General Public License 
# as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later 
# version.
#
# Skarphed is distributed in the hope that it will be 
# useful, but WITHOUT ANY WARRANTY; without even the implied 
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public 
# License along with Skarphed. 
# If not, see http://www.gnu.org/licenses/.
###########################################################

from json import JSONDecoder, JSONEncoder

class AJAXHandler(object):
    """
    This shit handles all shit that is AJAX and shit
    """
    def __init__(self, core, callstring):
        """
        Initialize
        """
        self._core = core

        decoder = JSONDecoder()
        call = decoder.loads(callstring)

        self._widget_id = call["w"]
        self._params = {}
        if call.has_key("p") and type(call["p"]) == dict:
            self._params.update(call["p"])

    def get_answer(self):
        """
        Handles an AJAX call
        """
        module_manager = self._core.get_module_manager()
        widget = module_manager.get_widget(self._widget_id)
        html = widget.render_html(self._params)
        js   = widget.render_javascript(self._params)
        answer = {'h':html, 'j':js}
        encoder = JSONEncoder()
        answer = encoder.dumps(answer)
        return answer

AJAXScript = """
(function() {
  var SkdAJAX, SkdAjax,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  SkdAjax = {
    constructor: function() {
      if (typeof this.XMLHttpRequest === "undefined") {
        console.log('XMLHttpRequest is undefined');
        return this.XMLHttpRequest = function() {
          var error;
          try {
            return new ActiveXObject("Msxml2.XMLHTTP.6.0");
          } catch (_error) {
            error = _error;
          }
          try {
            return new ActiveXObject("Msxml2.XMLHTTP.3.0");
          } catch (_error) {
            error = _error;
          }
          try {
            return new ActiveXObject("Microsoft.XMLHTTP");
          } catch (_error) {
            error = _error;
          }
          throw new Error("This browser does not support XMLHttpRequest.");
        };
      }
    },
    execute_action: function(jsonstring) {
      var action, actionlist, _i, _len, _results;
      actionlist = JSON.parse(jsonstring);
      _results = [];
      for (_i = 0, _len = actionlist.length; _i < _len; _i++) {
        action = actionlist[_i];
        _results.push(this.single_action(action));
      }
      return _results;
    },
    single_action: function(action) {
      var req;
      req = new XMLHttpRequest();
      req.targetSpace = action.s;
      req.addEventListener('readystatechange', function() {
        var space, success_resultcodes, _ref;
        if (req.readyState === 4) {
          success_resultcodes = [200, 304];
          if (_ref = req.state, __indexOf.call(success_resultcodes, _ref) >= 0) {
            space = document.getElementById(req.targetSpace);
            return space.innerHTML = req.responseText;
          } else {
            return console.log("Error Loading File");
          }
        }
      });
      delete action.s;
      req.open('GET', '/ajax/' + JSON.toString(action));
      return req.send();
    }
  };

  SkdAJAX = new SkdAjax();

}).call(this);
"""