'''
Permissions handler.
'''
from pygdv.model import DBSession, Permission

def get_permissions(admin):
    '''
    Get the right permissions for an user.
    @param admin : True if the user is an admin.
    @type admin : a boolean.
    '''
    if admin :
        return DBSession.query(Permission).all()
    return DBSession.query(Permission).filter(Permission.name != 'admin').all()
