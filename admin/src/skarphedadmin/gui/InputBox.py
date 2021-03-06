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


import pygtk
pygtk.require("2.0")
import gtk

from skarphedadmin.glue.lng import _

class InputBox(gtk.Frame):
    def __init__(self,par,text,callback,typeWanted=False,notEmpty=False,cancel=True):
        self.par = par
        gtk.Frame.__init__(self, _("Input Box")) # TODO title
        
        self.set_border_width(10)
        
        self.label = gtk.Label(text)
        self.entry = gtk.Entry()
        self.space = gtk.Label()
        self.ok = gtk.Button(stock=gtk.STOCK_OK)
        if cancel:
            self.cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
        
        self.hbox = gtk.HBox()
        self.vbox = gtk.VBox()
        self.alignment = gtk.Alignment(0.5,0.5,0.1,0.05)

        self.hbox.pack_start(self.space,True)
        if cancel:
            self.hbox.pack_start(self.cancel,False)
        self.hbox.pack_start(self.ok,False)
        
        self.vbox.pack_start(self.label,True)
        self.vbox.pack_start(self.entry,False)
        self.vbox.pack_start(self.hbox,False)
        
        self.ok.connect("clicked", self.okCallback)
        if cancel:
            self.cancel.connect("clicked", self.cancelCallback)
        self.entry.connect("activate", self.okCallback)
        self.cb = callback
        self.typeWanted = typeWanted
        self.notEmpty = notEmpty
        
        self.alignment.add(self.vbox)
        self.add(self.alignment)
        self.getApplication().getMainWindow().openDialogPane(self)

        self.entry.grab_focus()
    
    def okCallback(self,widget=None,data=None):
        def errorMessage(msgId):
            msgs = (_("This is not a valid int number"),
                    _("Empty input is not valid")
                    )
            dia = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_WARNING, \
                                  buttons=gtk.BUTTONS_OK, message_format=msgs[msgId])
            dia.run()
            dia.destroy()
        
        value = self.entry.get_text()
        
        if self.notEmpty and value == "":
            errorMessage(1)
            return

        if self.typeWanted == int:
            try:
                value = int(value)
            except ValueError:
                errorMessage(0)
                return
        self.getApplication().getMainWindow().closeDialogPane()
        self.cb(value)
    
    def cancelCallback(self,widget=None, data=None):
        self.getApplication().getMainWindow().closeDialogPane()
        
    def getPar(self):
        return self.par

    def getApplication(self):
        return self.par.getApplication()
