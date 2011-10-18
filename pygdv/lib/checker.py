from pygdv.model import DBSession, Project, User, Track, Circle
from sqlalchemy.sql import and_




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
    return circle.creator_id == user_id