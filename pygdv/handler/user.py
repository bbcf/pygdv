# -*- coding: utf-8 -*-
"""user handler"""
from pygdv.model.auth import User
from pygdv.model import DBSession
from tg import abort
from sqlalchemy import and_

def get_user_in_session(request):
    '''
    Get the user that is performing the current request
    @param request: the web request
    @type request: a WebOb
    '''
    
    if not 'repoze.who.identity' in request.environ :
        abort(401)
    identity = request.environ['repoze.who.identity']
    email = identity['repoze.who.userid']
    user = DBSession.query(User).filter(User.email == email).first()
    return user

    
    
def get_user(key,mail):
    '''
    Get the user with the the given mail, 
    with the given key.
    '''
    return DBSession.query(User).filter(and_(User.email == mail, User.key == key)).first()
    
