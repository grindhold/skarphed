#!/usr/bin/python
#-*- coding: utf-8 -*-

###########################################################
# Copyright 2011 Daniel 'grindhold' Brendle and Team
#
# This file is part of Scoville.
#
# Scoville is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License 
# as published by the Free Software Foundation, either 
# version 3 of the License, or (at your option) any later 
# version.
#
# Scoville is distributed in the hope that it will be 
# useful, but WITHOUT ANY WARRANTY; without even the implied 
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public 
# License along with Scoville. 
# If not, see http://www.gnu.org/licenses/.
###########################################################

import sys
import os
from GenericObject import ObjectPageAbstract
from data.Generic import GenericObjectStoreException


import pygtk
pygtk.require("2.0")
import gtk

class WidgetPage(ObjectPageAbstract):
    def __init__(self,par,widget):
        ObjectPageAbstract.__init__(self, par, widget)

        self.widgetGuiLoaded = False

        self.label = gtk.Label("Wait a Second. Loading GUI")
        self.add(self.label)

        module = widget.getModule()
        
        if not module.isGuiAvailable():
            module.addCallback(self.render)
            module.loadGui()
        if not os.path.expanduser("~/.scovilleadmin/modulegui") in sys.path:
            sys.path.append(os.path.expanduser("~/.scovilleadmin/modulegui"))

        self.render()

    def render(self):
        widget = self.getMyObject()
        if not widget:
            return

        module = widget.getModule()

        if module.isGuiAvailable() and not self.widgetGuiLoaded:
            module.removeCallback(self.render)
            self.label.destroy()
            
            exec "from %s.%s.widget import WidgetPage as ImplementedWidgetPage"%(module.getModuleName(),
                                                                            module.getVersionFolderString())
            widgetPage = ImplementedWidgetPage(self, widget)
            self.add(widgetPage)
            self.show_all()
            self.widgetGuiLoaded = True
