#!/usr/bin/python

import gui
import data.Profile

class Application:
    STATE_LOGGEDIN = 1
    STATE_LOGGEDOUT = 0
    
    def __init__(self):
        self.mainwin= gui.MainWindow(self)
        self.state = self.STATE_LOGGEDOUT
        self.activeProfile=None
    
    def run(self):
        gui.run()
    
    def logout(self):
        self.activeProfile.save()
        del(self.activeProfile)
        self.state = self.STATE_LOGGEDOUT
    
    def doLoginTry(self,username,password):
        profile = data.Profile.Profile(username,password)
        profile.load()
        self.state = self.STATE_LOGGEDIN
        self.activeProfile = profile
            
    def createProfile(self,username,password):
        profile = data.Profile.Profile(username,password)
        profile.create()
        self.state = self.STATE_LOGGEDIN
        self.activeProfile = profile
        
 
application = Application()
application.run()

        