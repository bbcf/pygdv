from pygdv.model import DBSession, Project, User
from sqlalchemy.sql import and_




def user_own_project(user_id, project_id):
    '''
    Look if the user own the project 
    '''
    project = DBSession.query(Project).filter(Project.id == project_id).first()
    return project.user_id == user_id