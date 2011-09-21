# -*- coding: utf-8 -*-
"""Setup the turbotequila application"""

from pygdv import model
from sqlalchemy.exc import IntegrityError
import transaction

group_admins = 'Admins'
perm_admin = 'admin'

group_users = 'Users'
perm_user = 'user'

right_write = 'write'
right_execute = 'execute'
right_read = 'read'
def bootstrap(command, conf, vars):
    """Place any commands to setup turbotequila here.
    Note that you will have to log in the application one before launching the bootstrap."""
    try:

        #admin = model.DBSession.query(model.User).filter(model.User.email == 'your_email_on_tequila@your_university.ch').first()
        admin = model.DBSession.query(model.User).filter(model.User.email == 'yohan.jarosz@epfl.ch').first()


        if admin:
            print 'Adding default groups and permissions'
            # ADMIN GROUP
            admins = model.Group()
            admins.name = group_admins
            admins.users.append(admin)
            model.DBSession.add(admins)
        
            # ADMIN PERMISSION
            perm = model.Permission()
            perm.name = perm_admin
            perm.description = u'This permission give admin right to the bearer'
            perm.groups.append(admins)
            model.DBSession.add(perm)
            transaction.commit()
        else :
            # USER GROUP
            users = model.Group()
            users.name = group_users
            model.DBSession.add(users)
            # READ PERMISSION
            read = model.Permission()
            read.name = perm_user
            read.description = u'This permission give "read" right to the bearer'
            read.groups.append(users)
            model.DBSession.add(read)
            # RIGHTS
            write = model.Right()
            write.name = right_write
            write.description = u'A group with this permission can upload/download tracks to the project'
            model.DBSession.add(write)
            
            execute = model.Right()
            execute.name = right_execute
            execute.description = u'A group with this permission can execute jobs on the project'
            model.DBSession.add(execute)
            
            read = model.Right()
            read.name = right_read
            read.description = u'A group with this permission can view the project'
            model.DBSession.add(read)
            
            transaction.commit()
            print '''
                    
                    Change email value in " turbotequila.websetup.bootstrap.py ".
                    Launch " paster serve --reload development.ini ".
                    Log in the application.
                    Re-run "python setup-app development.ini". 
                    It will gives you admin rights.
                    
                  '''
           
    except IntegrityError:
        print 'Warning, there was a problem adding your auth data, it may have already been added:'
        import traceback
        print traceback.format_exc()
        transaction.abort()
        print 'Ending with bootstrapping...'
        
        
        
    