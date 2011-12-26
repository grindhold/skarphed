#!/usr/bin/python
#-*- coding: utf-8 -*-

import pygtk
pygtk.require("2.0")
import gtk

import IconStock

from ServerPropertyWindow import ServerPropertyWindow

class TreeContextMenu(gtk.Menu):
    def __init__(self,parent):
        gtk.Menu.__init__(self)

        self.par = parent
        self.concernedIter = None

        removeServerI = gtk.Image()
        connectServerI = gtk.Image()
        propertiesI = gtk.Image()
        
        removeServerI.set_from_pixbuf(IconStock.DELETE)
        connectServerI.set_from_pixbuf(IconStock.SCOVILLE)
        propertiesI.set_from_pixbuf(IconStock.SCOVILLE)
        
        self.removeServer = gtk.ImageMenuItem()
        self.connectServer = gtk.ImageMenuItem()
        self.properties = gtk.ImageMenuItem()
        
        self.removeServer.set_image(removeServerI)
        self.connectServer.set_image(connectServerI)
        self.properties.set_image(propertiesI)

        gtk.MenuItem.__init__(self.removeServer,"Remove Server")
        gtk.MenuItem.__init__(self.connectServer,"Attempt Connection")
        gtk.MenuItem.__init__(self.properties, "Properties...")
        
        self.append(self.removeServer)
        self.append(self.connectServer)
        self.append(self.properties)

        self.show_all()
        self.removeServer.connect("activate",self.cb_removeServer)
        self.connectServer.connect("activate", self.cb_connectServer)
        self.properties.connect("activate", self.cb_Properties)

    def cb_removeServer(self,data=None):
        self.currentObject.destroy()
  
    def cb_connectServer(self,data=None):
        self.currentObject.establishConnections()
        
    def cb_Properties(self,data=None):
        if self.currentObject.__class__.__name__ == "Server":
            ServerPropertyWindow(self.getPar().getPar(),server=self.currentObject)
        
    def popup(self,obj,button,time):
        if obj.__class__.__name__ == "Server":
            self.connectServer.set_sensitive(not obj.isOnline())
        elif obj.__class__.__name__ == "GenericScovilleObject":
            pass
        else: 
            return
        self.currentObject = obj
        gtk.Menu.popup(self,None,None,None,button,time,None)
    
    def getPar(self):
        return self.par

    def getApplication(self):
        return self.par.getApplication()