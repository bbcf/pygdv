from pygdv.model import DBSession, Circle, User
from sqlalchemy.sql import and_

def create(name, description, creator_id, users=None):
    '''
    Create a new circle.
    @param name : the name
    @param description : the descrition
    @param creator_id : the identifier of the user creating the circle
    @param users : a list of users
    '''
    c = Circle()
    c.name = name
    c.description = description
    c.creator_id = creator_id
    if users is not None:
        for user_id in users :
            u = DBSession.query(User).filter(User.id == user_id).first()
            c.users.append(u)
    DBSession.add(c)
    DBSession.flush()
    
def create_admin(name):
    '''
    Create a new admin circle.
    @param name : the name
    '''
    c = Circle()
    c.name = name
    c.description = 'Circle created with Tequila'
    c.admin = True
    DBSession.add(c)
    DBSession.flush()
    return c

def get_tequila_circle(name):
    '''
    Get the Circle created by Tequila with the specified name
    @param name : the name
    '''
    return DBSession.query(Circle).filter(and_(Circle.admin == True, Circle.name == name)).first()