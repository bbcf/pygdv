# -*- coding: utf-8 -*-
"""Login controller."""

from pygdv.lib.base import BaseController
from pygdv.lib import tequila, constants
from tg import expose,url,flash,request,response
from tg.controllers import redirect
from pygdv.model import User, Group, DBSession
from paste.auth import auth_tkt
from pygdv.config.app_cfg import token
from paste.request import resolve_relative_url
import transaction
import datetime
from tg import app_globals as gl
import tg
from pygdv import handler

__all__ = ['LoginController']



class LoginController(BaseController):

   
    @expose('pygdv.templates.index')
    def index(self):
        '''
        Redirect user on tequila page in order to log him
        '''
        u = resolve_relative_url(url(), request.environ)
        res = tequila.create_request(u+'/login/auth','tequila.epfl.ch')
        raise redirect('https://tequila.epfl.ch/cgi-bin/tequila/requestauth?request'+res)
        

    @expose('pygdv.templates.index')
    def auth(self,came_from='/',**kw):
        '''
        Fetch user back from tequila.
        Validate the key from tequila.
        Log user.
        '''
        if not kw.has_key('key'):
            raise redirect(came_from)

        # take parameters
        key = kw.get('key')
        environ = request.environ
        authentication_plugins = environ['repoze.who.plugins']
        identifier = authentication_plugins['ticket']
        secret = identifier.secret
        cookiename = identifier.cookie_name
        remote_addr = environ['REMOTE_ADDR']
        # get user
        principal = tequila.validate_key(key,'tequila.epfl.ch')
        if principal is None:
            raise redirect('/login')
        tmp_user = self.build_user(principal)
        mail = tmp_user.email
        # log or create him
        user = DBSession.query(User).filter(User.email == tmp_user.email).first()
        if user is None:
            user_group = DBSession.query(Group).filter(Group.name == constants.group_users).first()
            user_group.users.append(tmp_user)
            DBSession.add(tmp_user)
            DBSession.flush()
            #transaction.commit()
            user = DBSession.query(User).filter(User.email == mail).first()
            flash( '''Your account has been created: %s'''%( user, ))
            DBSession.flush()
            self.build_circles_with_user(tmp_user, principal)
            DBSession.flush()
            #transaction.commit()
        elif user.name == constants.tmp_user_name:
            user.name = tmp_user.name
            user._set_date(datetime.datetime.now())
            user_group = DBSession.query(Group).filter(Group.name == constants.group_users).first()
            user_group.users.append(tmp_user)
            flash( '''Your account has been created: %s'''%( user, ))
            DBSession.add(user)
            DBSession.flush()
            self.build_circles_with_user(tmp_user, principal)
            DBSession.flush()
            #transaction.commit()
        else :
            flash( '''Welcome back: %s'''%( user, ), 'notice')
            self.check_circles_with_user(user, principal)
        
        # look if an user is admin or not
        admins = tg.config.get('admin.mails')
        group_admins = DBSession.query(Group).filter(Group.name == constants.group_admins).first()
        if user.email in admins:
            user not in group_admins.users and group_admins.users.append(user)
        else :
            user in group_admins.users and group_admins.users.remove(user)
        DBSession.flush()
        # create the authentication ticket
        user = DBSession.query(User).filter(User.email == mail).first()
        userdata=str(user.id)
        ticket = auth_tkt.AuthTicket( 
                                       secret, user.email, remote_addr, tokens=token, 
                                       user_data=userdata, time=None, cookie_name=cookiename, 
                                       secure=True) 
        val = ticket.cookie_value()
        # set it in the cookies
        response.set_cookie(
                     cookiename, 
                     value=val, 
                     max_age=None, 
                     path='/', 
                     domain=None, 
                     secure=False, 
                     httponly=False, 
                     comment=None, 
                     expires=None, 
                     overwrite=False)
        transaction.commit()
        raise redirect(came_from)
      
    @expose('pygdv.templates.index')
    def out(self):
        '''
        Logout the user.
        '''
        environ = request.environ
        authentication_plugins = environ['repoze.who.plugins']
        identifier = authentication_plugins['ticket']
        cookiename = identifier.cookie_name
        response.delete_cookie(cookiename)
        raise redirect(url())
    
    
    def build_user(self,principal):
        '''
        Build an User from a principal hash from Tequila
        @param principal: the hash from Tequila
        @return: an User
        '''
        hash = dict(item.split('=') for item in principal.split('\n') if len(item.split('='))>1)
        user = User()
        if(hash.has_key('name')):
            user.name = hash.get('name')
        if(hash.has_key('email')):
            user.email = hash.get('email')
        if(hash.has_key('firstname')):
            user.firstname = hash.get('firstname')
        return user
    
    def build_circles_with_user(self, user, principal):
        '''
        Build the groups that are in tequila and add the user to it.
        Must use the ``fake user``
        '''
        hash = dict(item.split('=') for item in principal.split('\n') if len(item.split('='))>1)
        if(hash.has_key('allunits')):
            group_list = hash.get('allunits').split(',')
            for group_name in group_list:
                circle = handler.circle.get_tequila_circle(group_name)
                if circle is None:
                    circle = handler.circle.create_admin(group_name)
                circle.users.append(user)
                DBSession.flush()
                    
                    
    def check_circles_with_user(self, user, principal):
        
        '''
        Check if the groups that are in tequila and add the user to it.
        This method is here because at first, circles was not created with `allunits` parameters but with `groups`
        one. So users that are logged already must be re-added to the right groups
        '''
        hash = dict(item.split('=') for item in principal.split('\n') if len(item.split('='))>1)
        if(hash.has_key('allunits')):
            group_list = hash.get('allunits').split(',')
            for group_name in group_list:
                circle = handler.circle.get_tequila_circle(group_name)
                if circle is None:
                    circle = handler.circle.create_admin(group_name)
                circle.users.append(user)
                DBSession.flush()
                    
                    
                    
                    
                    
                    
                    
                    
    