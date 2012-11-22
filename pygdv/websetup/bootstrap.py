# -*- coding: utf-8 -*-
"""Setup the pygdv application"""

from pygdv import model
from sqlalchemy.exc import IntegrityError
import transaction
from pygdv.lib import constants
import os


def bootstrap(command, conf, vars):
    """Place any commands to setup turbotequila here.
    Note that you will have to log in the application one before launching the bootstrap."""
    try:
            print '[pygdv] [DATABASE] Adding default groups and permissions'
            print '[pygdv] [bootstrap] Adding default groups and permissions'
            # ADMIN GROUP
            admins = model.Group()
            admins.name = constants.groups['admin']['name']
            admins.id = constants.groups['admin']['id']
            model.DBSession.add(admins)

            # USER GROUP
            users = model.Group()
            users.name = constants.groups['user']['name']
            users.id = constants.groups['user']['id']
            model.DBSession.add(users)

            # ADMIN PERMISSION
            perm = model.Permission()
            perm.id = constants.permissions['admin']['id']
            perm.name = constants.permissions['admin']['name']
            perm.description = constants.permissions['admin']['desc']
            perm.groups.append(admins)
            model.DBSession.add(perm)

            # READ PERMISSION
            read = model.Permission()
            read.id = constants.permissions['read']['id']
            read.name = constants.permissions['read']['name']
            read.description = constants.permissions['read']['desc']
            read.groups.append(users)
            model.DBSession.add(read)

            # RIGHTS
            write = model.Right()
            write.id = constants.rights['upload']['id']
            write.name = constants.rights['upload']['name']
            write.description = constants.rights['upload']['desc']
            model.DBSession.add(write)

            execute = model.Right()
            execute.id = constants.rights['download']['id']
            execute.name = constants.rights['download']['name']
            execute.description = constants.rights['download']['desc']
            model.DBSession.add(execute)

            read = model.Right()
            read.id = constants.rights['read']['id']
            read.name = constants.rights['read']['name']
            read.description = constants.rights['read']['desc']
            model.DBSession.add(read)

            print '[pygdv] [bootstrap] Adding admin user'
            u = model.User()
            u.id = constants.admin_user['id']
            u.name = constants.admin_user['name']
            u.firstname = constants.admin_user['firstname']
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
