# -*- coding: utf-8 -*-

"""The application's Globals object"""
#from pygdv.websetup.bootstrap import group_admins, group_users, perm_admin, perm_user
__all__ = ['Globals']



from pygdv.lib import constants
from bbcflib.genrep import GenRep
# CIRCLE & RIGHTS configuration


 

 
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
        self.group_admins = constants.group_admins
        self.group_users = constants.group_users
        self.perm_user = constants.perm_user
        self.perm_admin = constants.perm_admin
        self.right_upload = constants.right_upload
        self.right_download = constants.right_download
        self.right_read = constants.right_read
        
        self.genrep = GenRep()
        
        self.plugin_manager = init_plugins()
        
        
def init_plugins():
    from yapsy.PluginManager import PluginManager
    manager = PluginManager()
    manager.setPluginPlaces([constants.plugin_directory()])
    manager.collectPlugins()
    for plug in manager.getAllPlugins():
        try :
            test_plugin(plug)
        except NotImplementedError as e:
            print "[WARNING] plugin " + plug.name + " will not work"
    return manager    
        
def test_plugin(plugin):
    plug = plugin.plugin_object
    plug.title()
    plug.path()
    plug.output()
    
    
    
        