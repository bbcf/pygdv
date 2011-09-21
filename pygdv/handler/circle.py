from pygdv.model import DBSession, Circle, User

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
            c.users.append(user_id)
            u = DBSession.query(User).filter(User.id == user_id).first()
            c.users.append(u)
    DBSession.add(c)
    DBSession.flush()