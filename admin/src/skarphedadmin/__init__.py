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


import skarphedadmin.gui
import skarphedadmin.data.Generic
import skarphedadmin.data.Profile
import skarphedadmin.glue.threads
import skarphedadmin.net.SSH
import os
import logging
from skarphedcommon.errors import getAppropriateException

from skarphedadmin.glue.autosave import AutoSaveThread

class ApplicationException(Exception): pass

class Application(object):
    STATE_LOGGEDIN = 1
    STATE_LOGGEDOUT = 0
    
    def __init__(self):
        os.environ['PYGTK_FATAL_EXCEPTIONS'] = '1'
        skarphedadmin.data.Generic.setApplicationReference(self)
        self.mainwin = skarphedadmin.gui.MainWindow(self)
        self.quitrequest = False
        self.tracker = skarphedadmin.glue.threads.Tracker(self)
        self.tracker.start()
        self.state = self.STATE_LOGGEDOUT
        self.activeProfile=None
        self.instanceTypes = []
        
        if not os.path.exists(os.path.expanduser('~/.skarphedadmin/')):
            os.mkdir(os.path.expanduser('~/.skarphedadmin/'))

        logging.basicConfig(filename=os.path.expanduser('~/.skarphedadmin/generic.log'),level=logging.DEBUG)
        AutoSaveThread(self).start()

        
        from data import skarphed
    
    def run(self):
        try:
            skarphedadmin.gui.run()
        except KeyboardInterrupt, e:
            self.mainwin.cb_Close()
        
    def logout(self):
        if self.state == self.STATE_LOGGEDIN:
            self.activeProfile.updateProfile()
            self.activeProfile.save()
            skarphedadmin.data.Generic.ObjectStore().clear()
            del(self.activeProfile)
            self.state = self.STATE_LOGGEDOUT
        else:
            raise ApplicationException("Already logged out")
    
    def doLoginTry(self,username,password):
        if self.state == self.STATE_LOGGEDOUT:
            profile = skarphedadmin.data.Profile.Profile(username,password)
            profile.load()
            self.state = self.STATE_LOGGEDIN
            self.activeProfile = profile
            
    def createProfile(self,username,password):
        if self.state == self.STATE_LOGGEDOUT:
            profile = skarphedadmin.data.Profile.Profile(username,password)
            profile.create()
            self.state = self.STATE_LOGGEDIN
            self.activeProfile = profile
    
    def setQuitRequest(self,val):
        self.quitrequest = val
    
    def raiseRPCException(self, exception):
        raise exception

    def getSSHConnection(self,server):
        skarphedadmin.net.SSH.SSHConnector(server).start()
    
    def getObjectStore(self):
        return skarphedadmin.data.getObjectStore()
    
    def getData(self):
        return skarphedadmin.data

    def getMainWindow(self):
        return self.mainwin
    
    def getLocalObjectById(self,obj_id):
        return self.getObjectStore().getLocalObjectById(obj_id)
    
    def registerInstanceType(self, instancetype):
        self.instanceTypes.append(instancetype)
        
    def getInstanceTypes(self):
        return self.instanceTypes
    
    def createServerFromInstanceUrl(self, instanceurl):
        return skarphedadmin.data.createServerFromInstanceUrl(instanceurl)

if __name__=="__main__":
    application = Application()
    application.run()

        
