# -*- coding: utf-8 -*-
"""Login controller."""

from pygdv.lib.base import BaseController
from pygdv.lib import tequila, constants
from tg import expose, url, flash, request, response
from tg.controllers import redirect
from pygdv.model import User, Group, DBSession
from paste.auth import auth_tkt
from pygdv.config.app_cfg import token
from paste.request import resolve_relative_url
import transaction
import datetime
import tg
from pygdv import handler

__all__ = ['LoginController']


class LoginController(BaseController):

    @expose('pygdv.templates.index')
    def index(self, came_from='/'):
        '''
        Redirect user on tequila page in order to log him
        '''
        if tg.config.get('authentication.disable').lower() in ['t', 'true']:
            print constants.admin_user_email()

            environ = request.environ
            authentication_plugins = environ['repoze.who.plugins']
            identifier = authentication_plugins['ticket']
            secret = identifier.secret
            cookiename = identifier.cookie_name
            remote_addr = environ['REMOTE_ADDR']
            user = DBSession.query(User).filter(User.email == constants.admin_user_email()).first()
            admins = tg.config.get('admin.mails')
            group_admins = DBSession.query(Group).filter(Group.id == constants.group_admins_id).first()
            if user.email in admins:
                user not in group_admins.users and group_admins.users.append(user)
            else:
                user in group_admins.users and group_admins.users.remove(user)
            DBSession.flush()
            userdata = "%s|%s" % (user.id, user in group_admins.users)

            ticket = auth_tkt.AuthTicket(
                secret, user.email, remote_addr, tokens=token,
                user_data=userdata, time=None, cookie_name=cookiename,
                secure=True)

            val = ticket.cookie_value()
            # set it in the cookies
            response.set_cookie(
                cookiename, value=val, max_age=None, path='/', domain=None, secure=False,
                httponly=False, comment=None, expires=None, overwrite=False)
            raise redirect(came_from)

        u = resolve_relative_url(url(), request.environ)
        res = tequila.create_request(u + '/login/auth', 'tequila.epfl.ch')
        raise redirect('https://tequila.epfl.ch/cgi-bin/tequila/requestauth?request' + res)

    @expose('pygdv.templates.index')
    def auth(self, came_from='/', **kw):
        '''
        Fetch user back from tequila.
        Validate the key from tequila.
        Log user.
        '''
        if not 'key' in kw:
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
        principal = tequila.validate_key(key, 'tequila.epfl.ch')
        if principal is None:
            raise redirect('./login')
        tmp_user = self.build_user(principal)
        mail = tmp_user.email
        # log or create him
        user = DBSession.query(User).filter(User.email == tmp_user.email).first()
        if user is None:
            user_group = DBSession.query(Group).filter(Group.id == constants.group_users_id).first()
            user_group.users.append(tmp_user)
            DBSession.add(tmp_user)
            DBSession.flush()
            #transaction.commit()
            user = DBSession.query(User).filter(User.email == mail).first()
            flash('Your account has been created')
            DBSession.flush()
            self.build_circles_with_user(tmp_user, principal)
            DBSession.flush()
            #transaction.commit()
        elif user.name == constants.tmp_user_name:
            user.name = tmp_user.name
            user.firstname = tmp_user.firstname
            user._set_date(datetime.datetime.now())
            #user_group = DBSession.query(Group).filter(Group.id == constants.group_users_id).first()
            #user_group.users.append(tmp_user)
            flash('Your account has been created')
            DBSession.flush()
            self.build_circles_with_user(tmp_user, principal, user)
            DBSession.flush()
            #transaction.commit()
        else:
            flash('Welcome back', 'notice')
            self.check_circles_with_user(user, principal)

        # look if an user is admin or not
        admins = tg.config.get('admin.mails')
        group_admins = DBSession.query(Group).filter(Group.id == constants.group_admins_id).first()
        if user.email in admins:
            user not in group_admins.users and group_admins.users.append(user)
        else:
            user in group_admins.users and group_admins.users.remove(user)
        DBSession.flush()
        # create the authentication ticket
        user = DBSession.query(User).filter(User.email == mail).first()

        userdata = "%s|%s" % (user.id, user in group_admins.users)

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
        raise redirect('/')

    def build_user(self, principal):
        '''
        Build an User from a principal hash from Tequila
        @param principal: the hash from Tequila
        @return: an User
        '''
        hash = dict(item.split('=') for item in principal.split('\n') if len(item.split('=')) > 1)
        user = User()
        if 'name' in hash:
            user.name = hash.get('name')
        if 'email' in hash:
            user.email = hash.get('email')
        if 'firstname' in hash:
            user.firstname = hash.get('firstname')
        return user

    def build_circles_with_user(self, user, principal, u=None):
        '''
        Build the groups that are in tequila and add the user to it.
        Must use the ``fake user``
        '''
        hash = dict(item.split('=') for item in principal.split('\n') if len(item.split('=')) > 1)
        if 'allunits' in hash:
            group_list = hash.get('allunits').split(',')
            for group_name in group_list:
                circle = handler.circle.get_tequila_circle(group_name)
                if circle is None:
                    circle = handler.circle.create_admin(group_name)
                if u:
                    circle.users.append(u)
                else:
                    circle.users.append(user)
                DBSession.flush()

    def check_circles_with_user(self, user, principal):
        '''
        Check if the groups that are in tequila and add the user to it.
        This method is here because at first, circles was not created with `allunits` parameters but with `groups`
        one. So users that are logged already must be re-added to the right groups
        '''
        hash = dict(item.split('=') for item in principal.split('\n') if len(item.split('=')) > 1)
        if 'allunits' in hash:
            group_list = hash.get('allunits').split(',')
            for group_name in group_list:
                circle = handler.circle.get_tequila_circle(group_name)
                if circle is None:
                    circle = handler.circle.create_admin(group_name)
                circle.users.append(user)
                DBSession.flush()
