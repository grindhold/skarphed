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

this.SkdAJAX = 
    execute_action: (actionlist) ->
        this.single_action action for action in actionlist
        return undefined

    single_action: (action) ->
        if (typeof @XMLHttpRequest == "undefined")
            console.log 'XMLHttpRequest is undefined'
            @XMLHttpRequest = ->
                try
                    return new ActiveXObject("Msxml2.XMLHTTP.6.0")
                catch error
                try
                    return new ActiveXObject("Msxml2.XMLHTTP.3.0")
                catch error
                try
                    return new ActiveXObject("Microsoft.XMLHTTP")
                catch error
                throw new Error("This browser does not support XMLHttpRequest.")

        req = new XMLHttpRequest()
        req.targetSpace = action.s
        req.widgetId = action.w
        req.addEventListener 'readystatechange', ->
            if req.readyState is 4
                success_resultcodes = [200,304]
                if req.status in success_resultcodes
                    space = document.getElementById "space_"+req.targetSpace
                    widget_script = document.getElementById req.widgetId+"_scr"
                    response = JSON.parse req.responseText
                    space.innerHTML = response.h
                    widget_script.innerHTML = response.j
                else
                    console.log "Error Loading Content"
        delete(action.s)
        url = '/ajax/'+JSON.stringify (action)
        req.open 'GET', url, true
        req.send null
