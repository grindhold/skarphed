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

from skd_test import CoreTestCase
from skd_test import LIBPATH
import sys
sys.path.append(LIBPATH)

from common.errors import PermissionException, UserException

class TestPermissionFunctions(CoreTestCase):
    def setUp(self):
        CoreTestCase.setUp(self)
        # permission_manager = self._core.get_permission_manager()
        # self.testrole = permission_manager.create_role({"name":"testrole2"})
        # self.testpermission = permission_manager.create_permission("testpermission","test_module")

    def test_create_delete_role(self):
        permission_manager = self._core.get_permission_manager()
        role = permission_manager.create_role({"name":"testrole2"})

        role_id = role.get_id()
        role2 = permission_manager.get_role(role_id)
        self.assertEqual(role.get_name(),role2.get_name())

        try:
            role3 = permission_manager.create_role({"name":"testrole2"})
        except PermissionException:
            pass
        else:
            self.assertFail()

        role.delete()
        try:
            role3 = permission_manager.get_role(role_id)
        except PermissionException:
            pass
        else:
            self.assertFail()

    def test_create_delete_permission(self):
        permission_manager = self._core.get_permission_manager()
        permission = permission_manager.create_permission("testpermission2","test_module")

        self.assertIsNotNone(permission_manager.get_id_for_permission(permission))

        permission_manager.remove_permission(permission)

        self.assertIsNone(permission_manager.get_id_for_permission(permission))

    def test_permission_assign_user_legal(self):
        """
        Sessionuser assigns permission to a user that he owns himself (shoud succeed)
        """
        user_manager = self._core.get_user_manager()
        session_user = user_manager.create_user("session_user","password")
        session_manager = self._core.get_session_manager()
        session = session_manager.create_session(session_user)
        session_manager.set_current_session(session)
        permission_manager = self._core.get_permission_manager()
        permission1 = permission_manager.create_permission("lel","some_module")
        session_user.grant_permission(permission1,ignore_check=True)

        user = user_manager.create_user("user","password")
        user.grant_permission(permission1)
        self.assertTrue(user.check_permission(permission1))
        user.delete()

        session_manager.set_current_session(None)
        session.delete()
        session_user.delete()
        permission_manager.remove_permission(permission1)

    def test_permission_assign_user_illegal(self):
        """
        Sessionuser assigns permission to a user that he does not own (should fail)
        """
        user_manager = self._core.get_user_manager()
        session_user = user_manager.create_user("session_user","password")
        session_manager = self._core.get_session_manager()
        session = session_manager.create_session(session_user)
        session_manager.set_current_session(session)
        permission_manager = self._core.get_permission_manager()
        permission1 = permission_manager.create_permission("lel","some_module")

        user = user_manager.create_user("user", "password")
        try:
            user.grant_permission(permission1)
        except UserException:
            pass
        else:
            self.assertFail()
        self.assertFalse(user.check_permission(permission1))
        user.delete()

        session_manager.set_current_session(None)
        session.delete()
        session_user.delete()
        permission_manager.remove_permission(permission1)

    def test_permission_assign_role_legal(self):
        """
        Sessionuser assigns permission to a role that he owns himself (should succeed)
        """
        user_manager = self._core.get_user_manager()
        session_user = user_manager.create_user("session_user","password")
        session_manager = self._core.get_session_manager()
        session = session_manager.create_session(session_user)
        session_manager.set_current_session(session)
        permission_manager = self._core.get_permission_manager()
        permission1 = permission_manager.create_permission("lel","some_module")
        session_user.grant_permission(permission1,ignore_check=True)

        role = permission_manager.create_role({"name":"role1"})
        role.add_permission(permission1)
        self.assertTrue(role.has_permission(permission1))
        role.delete()

        session_manager.set_current_session(None)
        session.delete()
        session_user.delete()
        permission_manager.remove_permission(permission1)

    def test_permission_assign_role_illegal(self):
        """
        Sessionuser assigns permission to a role that he does not own (should fail)
        """
        user_manager = self._core.get_user_manager()
        session_user = user_manager.create_user("session_user","password")
        session_manager = self._core.get_session_manager()
        session = session_manager.create_session(session_user)
        session_manager.set_current_session(session)
        permission_manager = self._core.get_permission_manager()
        permission1 = permission_manager.create_permission("lel","some_module")
        
        role = permission_manager.create_role({"name":"role1"})
        try:
            role.add_permission(permission1)
        except PermissionException:
            pass
        else:
            self.assertFail()
        self.assertFalse(role.has_permission(permission1))
        role.delete()

        session_manager.set_current_session(None)
        session.delete()
        session_user.delete()
        permission_manager.remove_permission(permission1)

    def test_permission_revoke_user_legal(self):
        """
        Sessionuser revokes permission from user that he owns himself (should succeed)
        """
        user_manager = self._core.get_user_manager()
        session_user = user_manager.create_user("session_user","password")
        session_manager = self._core.get_session_manager()
        session = session_manager.create_session(session_user)
        session_manager.set_current_session(session)
        permission_manager = self._core.get_permission_manager()
        permission1 = permission_manager.create_permission("lel","some_module")
        session_user.grant_permission(permission1,ignore_check=True)

        user = user_manager.create_user("user","password")
        user.grant_permission(permission1)
        self.assertTrue(user.check_permission(permission1))
        user.revoke_permission(permission1)
        self.assertFalse(user.check_permission(permission1))
        user.delete()

        session_manager.set_current_session(None)
        session.delete()
        session_user.delete()
        permission_manager.remove_permission(permission1)

    def test_permission_revoke_user_illegal(self):
        """
        Sessionuser revokes permission from user that he does not own (should fail)
        """
        user_manager = self._core.get_user_manager()
        session_user = user_manager.create_user("session_user","password")
        session_manager = self._core.get_session_manager()
        session = session_manager.create_session(session_user)
        session_manager.set_current_session(session)
        permission_manager = self._core.get_permission_manager()
        permission1 = permission_manager.create_permission("lel","some_module")
        session_user.grant_permission(permission1,ignore_check=True)

        user = user_manager.create_user("user","password")
        user.grant_permission(permission1)
        self.assertTrue(user.check_permission(permission1))
        session_user.revoke_permission(permission1,ignore_check=True)
        try:
            user.revoke_permission(permission1)
        except UserException:
            pass
        else:
            self.assertFail()
        self.assertTrue(user.check_permission(permission1))
        user.delete()

        session_manager.set_current_session(None)
        session.delete()
        session_user.delete()
        permission_manager.remove_permission(permission1)

    def test_permission_revoke_role_legal(self):
        """
        Sessionuser revokes permission from role and posseses the permission (should succeed)
        """
        user_manager = self._core.get_user_manager()
        session_user = user_manager.create_user("session_user","password")
        session_manager = self._core.get_session_manager()
        session = session_manager.create_session(session_user)
        session_manager.set_current_session(session)
        permission_manager = self._core.get_permission_manager()
        permission1 = permission_manager.create_permission("lel","some_module")
        session_user.grant_permission(permission1,ignore_check=True)

        role = permission_manager.create_role({"name":"role1"})
        role.add_permission(permission1)
        self.assertTrue(role.has_permission(permission1))
        role.remove_permission(permission1)
        self.assertFalse(role.has_permission(permission1))
        role.delete()

        session_manager.set_current_session(None)
        session.delete()
        session_user.delete()
        permission_manager.remove_permission(permission1)

    def test_permission_revoke_role_illegal(self):
        """
        Sessionuser revokes permission from role and does not own the permission (should fail)
        """
        user_manager = self._core.get_user_manager()
        session_user = user_manager.create_user("session_user","password")
        session_manager = self._core.get_session_manager()
        session = session_manager.create_session(session_user)
        session_manager.set_current_session(session)
        permission_manager = self._core.get_permission_manager()
        permission1 = permission_manager.create_permission("lel","some_module")
        session_user.grant_permission(permission1,ignore_check=True)

        role = permission_manager.create_role({"name":"role1"})
        role.add_permission(permission1)
        self.assertTrue(role.has_permission(permission1))
        session_user.revoke_permission(permission1,ignore_check=True)
        try:
            role.remove_permission(permission1)
        except PermissionException:
            pass
        else:
            self.assertFail()
        self.assertTrue(role.has_permission(permission1))
        role.delete()

        session_manager.set_current_session(None)
        session.delete()
        session_user.delete()
        permission_manager.remove_permission(permission1)

    def test_role_assign_user_legal(self):
        """
        Sessionuser assigns role to a user and possesses all the permissions of the role (should succeed)
        """
        user_manager = self._core.get_user_manager()
        session_user = user_manager.create_user("session_user","password")
        session_manager = self._core.get_session_manager()
        session = session_manager.create_session(session_user)
        session_manager.set_current_session(session)
        permission_manager = self._core.get_permission_manager()
        permission1 = permission_manager.create_permission("lel","some_module")
        session_user.grant_permission(permission1,ignore_check=True)

        user = user_manager.create_user("user","password")
        role = permission_manager.create_role({"name":"role1"})
        role.add_permission(permission1)
        self.assertTrue(role.has_permission(permission1))
        user.assign_role(role)
        self.assertTrue(user.check_permission(permission1))
        role.delete()
        user.delete()

        session_manager.set_current_session(None)
        session.delete()
        session_user.delete()
        permission_manager.remove_permission(permission1)

    def test_role_assign_user_illegal(self):
        """
        Sessionuser assigns role to a user and does not possess all the permissions of the role (shouold fail)
        """
        user_manager = self._core.get_user_manager()
        session_user = user_manager.create_user("session_user","password")
        session_manager = self._core.get_session_manager()
        session = session_manager.create_session(session_user)
        session_manager.set_current_session(session)
        permission_manager = self._core.get_permission_manager()
        permission1 = permission_manager.create_permission("lel","some_module")
        session_user.grant_permission(permission1,ignore_check=True)

        user = user_manager.create_user("user","password")
        role = permission_manager.create_role({"name":"role1"})
        role.add_permission(permission1)
        self.assertTrue(role.has_permission(permission1))
        session_user.revoke_permission(permission1, ignore_check=True)
        try:
            user.assign_role(role)
        except PermissionException:
            pass
        else:
            self.assertFail()
        self.assertFalse(user.check_permission(permission1))
        role.delete()
        user.delete()

        session_manager.set_current_session(None)
        session.delete()
        session_user.delete()
        permission_manager.remove_permission(permission1)


    def test_role_selfassign_legal(self):
        """
        Session user assigns himself a role that accumulates rights he possesses himself (should succeed)
        """
        user_manager = self._core.get_user_manager()
        session_user = user_manager.create_user("session_user","password")
        session_manager = self._core.get_session_manager()
        session = session_manager.create_session(session_user)
        session_manager.set_current_session(session)
        permission_manager = self._core.get_permission_manager()
        permission1 = permission_manager.create_permission("lel","some_module")
        session_user.grant_permission(permission1,ignore_check=True)

        role = permission_manager.create_role({"name":"role1"})
        role.add_permission(permission1)
        self.assertTrue(role.has_permission(permission1))
        session_user.assign_role(role)
        self.assertTrue(session_user.check_permission(permission1))
        role.delete()

        session_manager.set_current_session(None)
        session.delete()
        session_user.delete()
        permission_manager.remove_permission(permission1)

    def test_role_selfassign_illegal(self):
        """
        Session user assigns himself a role that's rights he does not have (should fail)
        """
        user_manager = self._core.get_user_manager()
        session_user = user_manager.create_user("session_user","password")
        session_manager = self._core.get_session_manager()
        session = session_manager.create_session(session_user)
        session_manager.set_current_session(session)
        permission_manager = self._core.get_permission_manager()
        permission1 = permission_manager.create_permission("lel","some_module")
        session_user.grant_permission(permission1,ignore_check=True)

        role = permission_manager.create_role({"name":"role1"})
        role.add_permission(permission1)
        self.assertTrue(role.has_permission(permission1))
        session_user.revoke_permission(permission1,ignore_check=True)
        try:
            session_user.assign_role(role)
        except PermissionException:
            pass
        else:
            self.assertFail()
        self.assertFalse(session_user.check_permission(permission1))
        role.delete()

        session_manager.set_current_session(None)
        session.delete()
        session_user.delete()
        permission_manager.remove_permission(permission1)

    def test_su_revoke_root_permission(self):
        """
        Sessionuser tries to revoke right from rootuser (must never happen)
        """
        user_manager = self._core.get_user_manager()
        session_user = user_manager.create_user("session_user","password")
        session_manager = self._core.get_session_manager()
        session = session_manager.create_session(session_user)
        session_manager.set_current_session(session)
        permission_manager = self._core.get_permission_manager()
        permission1 = permission_manager.create_permission("lel","some_module")
        session_user.grant_permission(permission1,ignore_check=True)

        root = user_manager.get_user_by_name("root")
        try:
            root.revoke_permission(permission1)
        except UserException:
            pass
        else:
            self.assertFail()
        self.assertTrue(root.check_permission(permission1))

        session_manager.set_current_session(None)
        session.delete()
        session_user.delete()
        permission_manager.remove_permission(permission1)

    def tearDown(self):
        CoreTestCase.tearDown(self)
        # permission_manager = self._core.get_permission_manager()
        # permission_manager.remove_permission(self.testpermission)
        # self.testrole.delete()
