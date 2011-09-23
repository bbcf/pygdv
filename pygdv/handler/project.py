from pygdv.model import DBSession, Project, Track, Right, RightCircleAssociation
from tg import app_globals as gl
from sqlalchemy.sql import and_

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
    if tracks is not None:
        for track_id in tracks :
            t = DBSession.query(Track).filter(Track.id == track_id).first()
            project.tracks.append(t)
    
    if circles is not None: # adding circle with the read permission by default
        read_right = DBSession.query(Right).filter(Right.name == gl.right_read).first()
        for circle_id in circles :
            cr_assoc = DBSession.query(RightCircleAssociation).filter(
                                    and_(RightCircleAssociation.right_id == read_right.id,
                                         RightCircleAssociation.circle_id == circle_id)).first()
            if cr_assoc is None :
                cr_assoc = RightCircleAssociation()
                cr_assoc.circle_id = circle_id
                cr_assoc.right = read_right
                DBSession.add(cr_assoc)
            project._circle_right.append(cr_assoc)
        
    DBSession.add(project)
    DBSession.flush()
    
    