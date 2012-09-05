# -*- coding: utf-8 -*-
"""Setup the turbotequila application"""

from pygdv import model
from sqlalchemy.exc import IntegrityError
import transaction



from pygdv.lib.constants import right_upload, right_download, right_read, group_admins, perm_admin, group_users, perm_user
from pygdv.lib.constants import right_download_id, right_read_id, right_upload_id, group_users_id, group_admins_id
from pygdv.lib import constants
def bootstrap(command, conf, vars):
    """Place any commands to setup turbotequila here.
    Note that you will have to log in the application one before launching the bootstrap."""
    
    
    try:

            print 'Adding default groups and permissions'
            # ADMIN GROUP
            admins = model.Group()
            admins.name = group_admins
            admins.id = group_admins_id
            model.DBSession.add(admins)

            # USER GROUP
            users = model.Group()
            users.name = group_users
            users.id = group_users_id
            model.DBSession.add(users)
        
            # ADMIN PERMISSION
            perm = model.Permission()
            perm.name = perm_admin
            perm.description = u'This permission give admin right to the bearer.'
            perm.groups.append(admins)
            model.DBSession.add(perm)

            # READ PERMISSION
            read = model.Permission()
            read.name = perm_user
            read.description = u'This permission give "read" right to the bearer.'
            read.groups.append(users)
            model.DBSession.add(read)
            
            # RIGHTS
            write = model.Right()
            write.id = right_upload_id
            write.name = right_upload
            write.description = u'A group with this permission can upload tracks to the project and execute jobs on the web interface.'
            model.DBSession.add(write)
            
            execute = model.Right()
            execute.id = right_download_id
            execute.name = right_download
            execute.description = u'A group with this permission can download files on a project.'
            model.DBSession.add(execute)
            
            read = model.Right()
            read.id = right_read_id
            read.name = right_read
            read.description = u'A group with this permission can view the project.'
            model.DBSession.add(read)
            
            print 'adding ADMIN user'
            u = model.User()
            u.name = 'user'
            u.firstname = 'admin'
            u.key = constants.admin_user_key()
            u.email = constants.admin_user_email()

            admins.users.append(u)
            users.users.append(u)
            
            model.DBSession.add(u)
            model.DBSession.add(users)
            model.DBSession.add(admins)
            
            transaction.commit()
           
    except IntegrityError:
        print 'Warning, there was a problem adding your auth data, it may have already been added:'
        import traceback
        print traceback.format_exc()
        transaction.abort()
        print 'Ending with bootstrapping...'
        
        
        
    