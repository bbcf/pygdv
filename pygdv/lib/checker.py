from pygdv.model import DBSession, Project, User, Track, Circle, Right, Group
from pygdv.lib import constants
from sqlalchemy.sql import and_, or_




def user_own_project(user_id, project_id):
    '''
    Look if the user own the project 
    '''
    project = DBSession.query(Project).filter(Project.id == project_id).first()
    return project.user_id == user_id


def user_own_track(user_id, track_id):
    '''
    Look if the user own the track 
    '''
    track = DBSession.query(Track).filter(Track.id == track_id).first()
    if track is not None : return track.user_id == user_id
    return False

def user_own_circle(user_id, circle_id):
    '''
    Look if the user own the circle.
    '''
    circle = DBSession.query(Circle).filter(Circle.id == circle_id).first()
    if circle.creator_id == user_id: return True
    if circle.admin :
        user = DBSession.query(User).filter(User.id == user_id).first()
        admin_group = DBSession.query(Group).filter(Group.name == constants.group_admins).first()
        return user in admin_group.users
    return False

def check_permission_project(user_id, project_id, right_id):
    if not user_own_project(user_id, project_id):
        print 'user does not own the project'
#        p1 = DBSession.query(Project).join(
#                                Project._circle_right).join(Right).join(User.circles).filter(
#                and_(User.id == user_id, Project.id == project_id, Right.id == right_id)
#                )
        p1 = DBSession.query(Project).join(
                                Project._circle_right).join(Right).filter(
                and_(Project.id == project_id, Right.id == right_id)
                )
        print p1
        p = p1.first()
        print p
        
        print 'project_circles'
        
        pc = DBSession.query(Project).filter(Project.id == project_id).first()
        print pc.circles_with_rights
        
        u = DBSession.query(User).filter(User.id == user_id).first()
        print u.circles
        
        
        
        return p != None
    return True

def can_download_track(user_id, track_id):
    if not user_own_track(user_id, track_id):
        t = DBSession.query(Track).join(Project.tracks).filter(
            and_(Track.id == track_id, User.id == user_id)
            
             ).first()
        return t != None
    return True
    


