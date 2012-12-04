# -*- coding: utf-8 -*-
"""user handler"""
from pygdv.model.auth import User, Group
from pygdv.model import DBSession, Project, RightCircleAssociation
from pygdv.lib import constants
from tg import abort
from sqlalchemy import and_


def get_user_in_session(request):
    '''
    Get the user that is performing the current request
    @param request: the web request
    @type request: a WebOb
    '''

    if not 'repoze.who.identity' in request.environ:
        abort(401)
    identity = request.environ['repoze.who.identity']
    email = identity['repoze.who.userid']
    user = DBSession.query(User).filter(User.email == email).first()
    return user


def get_user(key, mail):
    '''
    Get the user with the the given mail,
    with the given key.
    '''
    user = DBSession.query(User).filter(and_(User.email == mail, User.key == key)).first()
    return user


def create_tmp_user(mail):
    user = User()
    user.name = constants.tmp_user_name
    user.email = mail
    user.firstname = ''
    user_group = DBSession.query(Group).filter(Group.id == constants.group_users_id).first()
    user_group.users.append(user)
    DBSession.add(user)
    DBSession.flush()
    return user


def shared_projects(user_id, right_id):
    return DBSession.query(Project).join(RightCircleAssociation).join(User.circles).filter(
        and_(User.id == user_id, RightCircleAssociation.right_id == right_id)).all()


def shared_tracks(user_id, right_id):
    shared = []
    for project in shared_projects(user_id, right_id):
        shared.extend((t for t in project.tracks if t.user_id != user_id))
    return list(set(shared))
