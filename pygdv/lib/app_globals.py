# -*- coding: utf-8 -*-

"""The application's Globals object"""
#from pygdv.websetup.bootstrap import group_admins, group_users, perm_admin, perm_user
__all__ = ['Globals']

group_admins = 'Admins'
perm_admin = 'admin'

group_users = 'Users'
perm_user = 'user'

from bbcflib.genrep import GenRep

class Globals(object):
    """Container for objects available throughout the life of the application.

    One instance of Globals is created during application initialization and
    is available during requests via the 'app_globals' variable.

    """

    def __init__(self):
        '''
        @param tmp_pkg : the temporary directory in GDV as a package name
        @param tmp_user : the name of a temporary user
        '''
        self.tmp_pkg = 'pygdv.data.tmp'
        self.tmp_user_name = 'tmp_user'
        
        '''
        Default groups and permissions
        '''
        self.group_admins = group_admins
        self.group_users = group_users
        self.perm_user = perm_user
        self.perm_admin = perm_admin
        
        self.genrep = GenRep()
        
        