from pygdv.model import DBSession, Project, Track, Right, RightCircleAssociation, User, Circle
from tg import app_globals as gl
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.orm import aliased
from pygdv.lib import constants
from sqlalchemy.types import Boolean

def create(name, sequence_id, user_id, tracks=None, isPublic=False, circles=None):
    '''
    Create a new project.
    @param name: name of the project
    @param sequence_id: the sequence identifier
    @param user_id: the user identifier
    @param tracks: a list of tracks
    @param isPublic : if the project is public
    @param circles : a list of circles with 'read' permission
    '''
    edit(Project(), name, sequence_id, user_id, tracks, isPublic, circles)
    
def edit(project, name, sequence_id, user_id, tracks=None, isPublic=False, circles=None):
    '''
    Like create but edit an existing project.
    '''
    project.name=name
    project.sequence_id = sequence_id
    project.user_id = user_id
    project.is_public = isPublic
    DBSession.add(project)
    DBSession.flush()

    project.tracks = []
    if tracks is not None:
        for track_id in tracks :
            t = DBSession.query(Track).filter(Track.id == track_id).first()
            project.tracks.append(t)
    
    project._circle_right = []
    if circles is not None: # adding circle with the read permission by default
        for circle in circles : _add_read_right(project, circle.id)
        
    DBSession.add(project)
    DBSession.flush()



def change_rights(project_id, circle_id, rights=None):
    '''
    Modify the right associated to a project to a group.
    If any right is added, automatically add read right.
    @param project_id : the project id
    @param circle_id : the circle id
    @param rights : the right to update
    '''
    project = DBSession.query(Project).filter(Project.id == project_id).first()
    rc_assocs = get_circle_right_assocs(circle_id, project_id)
    
    
    for rc in rc_assocs:
        if rc.circle.id == int(circle_id) :
            project._circle_right.remove(rc)
   
    
    if rights is not None:
        _add_read_right(project, circle_id)
        for right_name in rights:
            if right_name != constants.right_read :
                right = DBSession.query(Right).filter(Right.name == right_name).first()
                cr_assoc = _get_circle_right_assoc(right, circle_id, project_id)
                project._circle_right.append(cr_assoc)
    DBSession.add(project)
    DBSession.flush()
    
def add_read_right_to_circles_ids(project, ids):
    '''
     Add the ``read`` right to the project & circles specified. Flush the database
    '''  
    for id in ids:
        _add_read_right(project, id)
    DBSession.add(project)
    DBSession.flush()
    
def add_read_right(project, circle_id):    
    '''
    Add the ``read`` right to the project & circle specified. Flush the database
    '''
    _add_read_right(project, circle_id)
    DBSession.add(project)
    DBSession.flush()
    
def _add_read_right(project, circle_id):    
    '''
    Add the ``read`` right to the project % circle specified without flushing
    '''
    read_right = DBSession.query(Right).filter(Right.name == gl.right_read).first()
    cr_assoc = _get_circle_right_assoc(read_right, circle_id, project.id)
    project._circle_right.append(cr_assoc)
    
    
def _get_circle_right_assoc(right, circle_id, project_id):
    '''
    Get the ``RightCircleAssociation`` corresponding
    to the right and circle_id and project_id given
    '''
    cr_assoc = DBSession.query(RightCircleAssociation).filter(
                                    and_(RightCircleAssociation.right_id == right.id,
                                         RightCircleAssociation.circle_id == circle_id,
                                         RightCircleAssociation.project_id == project_id
                                         )).first()
    if cr_assoc is None :
        cr_assoc = RightCircleAssociation()
        cr_assoc.circle_id = circle_id
        cr_assoc.right = right
        cr_assoc.project_id = project_id
        DBSession.add(cr_assoc)
    return cr_assoc

def get_circle_right_assocs(circle_id, project_id):
    '''
    Get the ``RightCircleAssociation`` corresponding
    to the circle_id & project_id given
    '''
    return DBSession.query(RightCircleAssociation).filter(
                        and_(RightCircleAssociation.circle_id == circle_id,
                            RightCircleAssociation.project_id == project_id)).all()
                            
                            
def add_tracks(project, track_ids):
    '''
    Add a list of track to the project specified.
    '''
    for track_id in track_ids:
        track = DBSession.query(Track).filter(Track.id == track_id).first()
        project.tracks.append(track)
    DBSession.add(project)
    DBSession.flush()
    
    
    
def get_projects_with_permission(user_id, right_name):
    right = DBSession.query(Right).filter(Right.name == right_name).first()
    return DBSession.query(Project).join(Project._circle_right).join(User.circles).filter(
                and_(User.id == user_id, Right.id == right.id)
                     ).all()
    
    

def get_shared_projects(user):
    '''
    Get the shared projects with rights associated which are not in the user projects.
    :return: {project: [rights,]}
    '''
    
    
    
    projects = DBSession.query(Project).distinct().join(
                                Project._circle_right).join(User.circles).filter(
                and_(User.id == user.id, or_(Right.id == constants.right_read_id, 
                                             Right.id == constants.right_upload_id, 
                                             Right.id == constants.right_download_id),
                     not_(Project.id.in_([p.id for p in user.projects])))
                     ).all()
    
    data = {}
    for project in projects:
        for circle, rights in project.circles_with_rights.iteritems():
            if circle in user.circles:
                if project not in data:
                    data[project] = []
                data[project]+= [right.name for right in rights if right.name not in data[project]]
    return data
    
    
    