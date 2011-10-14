# -*- coding: utf-8 -*-

"""The application's Globals object"""
#from pygdv.websetup.bootstrap import group_admins, group_users, perm_admin, perm_user
__all__ = ['Globals']



from bbcflib.genrep import GenRep
from pygdv.lib import constants

# CIRCLE & RIGHTS configuration

group_admins = 'Admins'
perm_admin = 'admin'

group_users = 'Users'
perm_user = 'user'


right_upload = 'Upload'
right_download = 'Download'
right_read = 'Read'
 

 
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
        self.public_dir = 'pygdv.public'
        self.data_dir = 'pygdv.data'
        self.tracks_dir = constants.tracks_dir
        self.json_dir = constants.json_dir
        
        '''
        Default groups and permissions
        '''
        self.group_admins = group_admins
        self.group_users = group_users
        self.perm_user = perm_user
        self.perm_admin = perm_admin
        self.right_upload = right_upload
        self.right_download = right_download
        self.right_read = right_read
        
        self.genrep = GenRep()
        
        
        
        
        