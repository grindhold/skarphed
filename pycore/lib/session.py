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

from hashlib import sha256
from datetime import datetime, timedelta
from random import randrange

class SessionException(Exception):
    ERRORS = {
        0:"""SessionError: Session Expired""",
        1:"""SessionError: Can only attach user to session""",
        2:"""SessionError: This Session does not exist"""
    }

    @classmethod
    def get_msg(cls,nr, info=""):
        return "SE_"+str(nr)+": "+cls.ERRORS[nr]+" "+info

class SessionManager(object):
    def __init__(self, core):
        self._core = core
        Session.set_core(core)

        self.get_session = Session.get_session
        self.create_session = Session.create_session

class Session(object):
    ACTIVE_SESSIONS = {}
    CURRENT_SESSION = None
    @classmethod
    def set_core(cls,core):
        cls._core = core

    @classmethod
    def get_session(cls,session_id):
        if not cls.ACTIVE_SESSIONS.has_key(session_id):
            raise SessionException(SessionException.get_msg(2))
        session = cls.ACTIVE_SESSIONS[session_id]
        if session._expiration < datetime.now():
            raise SessionException(SessionException.get_msg(0))
        else:
            return session

    @classmethod
    def create_session(cls, user):
        return Session(cls._core,user)

    def set_current_session(cls, session):
        cls.CURRENT_SESSION = session

    def get_current_session(cls):
        return cls.CURRENT_SESSION

    def _generateRandomString(self,length):
        ret = ""
        for i in range(length):
            x = -1
            while x in (-1,91,92,93,94,95,96,60,61,62,58,59,63,64):
                x = randrange(48,123)
            ret+=chr(x)
        return ret

    def __init__(self,core, user):
        self._core = core
        configuration = self._core.get_configuration() #TODO: Introduce Configvalue sessionduration

        self._id = sha256(self._generateRandomString(24)).hexdigest()
        self._user = user.get_id()
        self._expiration = datetime.now()+timedelta(0,int(configuration.get_entry("core.session_duration"))*3600)
        Session.ACTIVE_SESSIONS[self._id] = self

    def touch(self):
        configuration = self._core.get_configuration()
        self._expiration += timedelta(0,int(configuration.get_entry("core.session_extend"))*3600)

    def get_user(self):
        usermanager = self._core.get_user_manager()
        return usermanager.get_user(self._user)

    def set_user(self,user):
        if type(user) == int:
            self._user = user
        elif user.__class__.__name__ == "User":
            self._user = user.get_id()
        else:
            raise SessionException(SessionException.get_msg(1))