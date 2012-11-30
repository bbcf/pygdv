from pygdv.model import DBSession, Project, User, Track, Circle, Right, Group, Job
from pygdv.lib import constants
from sqlalchemy.sql import and_


def can_edit_track(user, track_id):
    for track in user.tracks:
        if int(track_id) == track.id:
            return True
    if is_admin(user):
        return True
    track = DBSession.query(Track).filter(Track.id == track_id).first()
    for project in track.projects:
        if check_permission(project=project, user=user, right_id=constants.right_upload_id):
            return True
    return False


def can_download_track(user_id, track_id):
    user = DBSession.query(User).filter(User.id == user_id).first()
    for track in user.tracks:
        if int(track_id) == track.id:
            return True
    if is_admin(user):
        return True
    track = DBSession.query(Track).filter(Track.id == track_id).first()
    for project in track.projects:
        if check_permission(project=project, user=user, right_id=constants.right_download_id):
            return True
    return False


def check_permission(project=None, project_id=None, user=None, user_id=None, right_id=None):
    """
    Check if an user can "right" the project
    """
    if project is None:
        project = DBSession.query(Project).filter(Project.id == project_id).first()
    if user is None:
        user = DBSession.query(User).filter(User.id == user_id).first()
    if project is None or user is None:
        return False
    if is_admin(user):
        return True
    if own(user=user, project=project):
        return True

    for circle, rights in project.circles_with_rights.iteritems():
        if right_id in [r.id for r in rights] and circle in user.circles:
            return True
    return False


def own(user=None, user_id=None, project=None, project_id=None):
    """
    Check if an user own a project
    """
    if user_id is None:
        user_id = user.id
    if project is None:
        project = DBSession.query(Project).filter(Project.id == project_id).first()
    return project.user_id == user_id


def is_admin(user):
    admin_group = DBSession.query(Group).filter(Group.id == constants.groups['admin']['id']).first()
    return user in admin_group.users


def user_own_track(user_id, track_id):
    '''
    Look if the user own the track
    '''
    track = DBSession.query(Track).filter(Track.id == track_id).first()
    if track is not None:
        return track.user_id == user_id
    return False


def user_own_circle(user_id, circle_id):
    '''
    Look if the user own the circle.
    '''
    circle = DBSession.query(Circle).filter(Circle.id == circle_id).first()
    if circle.creator_id == user_id:
        return True
    if circle.admin:
        user = DBSession.query(User).filter(User.id == user_id).first()
        admin_group = DBSession.query(Group).filter(Group.name == constants.group_admins).first()
        return user in admin_group.users
    return False



def can_edit_job(user_id, job_id):
    user = DBSession.query(User).filter(User.id == user_id).first()
    if is_admin(user):
        j = DBSession.query(Job).filter(and_(Job.id == job_id, Job.user_id == user_id)).first()
        return j != None
    return True
