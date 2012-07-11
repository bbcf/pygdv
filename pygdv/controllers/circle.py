"""Circle Controller"""
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate
from repoze.what.predicates import has_permission
from repoze.what.predicates import has_any_permission

from tg import expose, flash, require, request, tmpl_context, validate, url
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate ,with_trailing_slash, without_trailing_slash
from pygdv.lib.base import BaseController

from pygdv.model import DBSession, Circle, Species, User
from pygdv.widgets.circle import circle_table, circle_table_filler, circle_new_form, circle_edit_filler, circle_edit_form, circle_grid
from pygdv.widgets import datagrid, form
from pygdv import handler
from pygdv.lib import util, checker, constants
from sqlalchemy import and_
import genshi
import tw2.core as twc
import transaction

__all__ = ['CircleController']


class CircleController(BaseController):
    allow_only = has_any_permission(constants.perm_admin, constants.perm_user)

    def new(self, *args, **kw):
        widget = form.NewCircle(action=url('/circles/new')).req()
        if request.method == 'GET':
            return dict(page='circles', model='circle', widget=widget)
        else :
            try:
                widget.validate(kw)
            except twc.ValidationError as e:
                return dict(page='circles', model='circle', widget=e.widget)
        user = handler.user.get_user_in_session(request)
        handler.circle.create(kw['name'], kw['description'], user)
        raise redirect('/circles')

    @expose('pygdv.templates.circle_index')
    @with_trailing_slash
    def index(self, *args, **kw):
        kw['page']='circle'
        user = handler.user.get_user_in_session(request)

        data = util.to_datagrid(datagrid.circle_grid, user.circles_owned, grid_display=len(user.circles)>0)
        t = handler.help.tooltip['circle']

        widget = form.NewCircle(action=url('/circles/index')).req()
        if request.method == 'GET':
            return dict(page='circles', item=data, tooltip=t, widget=widget)
        else :
            try:
                widget.validate(kw)
            except twc.ValidationError as e:
                return dict(page='circles',  item=data, tooltip=t, widget=e.widget, ac_error=True)


        user = handler.user.get_user_in_session(request)
        handler.circle.create(kw['name'], kw['description'], user)


        return dict(page='circles', model='circle', item=data, widget=widget, tooltip=t)






    @expose()
    def delete(self, circle_id, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_circle(user.id, circle_id):
            flash('you have no right to delete this circle : you are not the creator of it')
            raise redirect('/circles')
        circle = DBSession.query(Circle).filter(Circle.id == circle_id).first()
        DBSession.delete(circle)
        DBSession.flush()
        raise redirect('/circles/')

    @expose()
    def delete_user(self, id, user_id):
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_circle(user.id, id):
            flash('you have no rights to delete users from this circle : you are not the creator of it')
            raise redirect('/circles')
        circle = DBSession.query(Circle).filter(Circle.id == id).first()
        to_delete = DBSession.query(User).filter(User.id == user_id).first()
        circle.users.remove(to_delete)
        DBSession.flush()
        raise redirect('/circles/edit/%s' % id)


    @expose('pygdv.templates.circle_edit')
    @with_trailing_slash
    def edit(self, *args, **kw):
        user = handler.user.get_user_in_session(request)

        t = handler.help.tooltip['circledesc']

        # get circle id
        if request.method == 'GET':
             circle_id = args[0]
        else :
            circle_id = kw.get('cid')
        circle_id=int(circle_id)
        print [c.id for c in user.circles_owned]
        if circle_id not in [c.id for c in user.circles_owned]:
            flash('You have no right to edit this circle', 'error')
            raise redirect('/circles/')
        circle = DBSession.query(Circle).filter(Circle.id == circle_id).first()
        widget = form.AddUser(action=url('/circles/edit/%s' % circle_id)).req()

        if request.method == 'POST':
            # add user
            mail = kw.get('mail')
            try:
                widget.validate({'cid' : circle_id, 'mail' : mail})
            except twc.ValidationError as e:
                for u in circle.users:
                    u.__dict__['cid'] = circle_id
                    wrappers = [u for u in circle.users if u.id != user.id]
                    data = [util.to_datagrid(datagrid.circle_description_grid, wrappers, grid_display=len(wrappers)>0)]
                return dict(page='circles', name=circle.name, widget=e.widget, items=data, value=kw, tooltip=t, au_error=True)

            to_add = DBSession.query(User).filter(User.email == mail).first()
            if to_add is None:
                to_add = handler.user.create_tmp_user(mail)
            handler.circle.add_user(circle_id=circle_id, user=to_add)

        # build common parameters
        if not checker.user_own_circle(user.id, circle_id):
            flash('you have no right to edit this circle : you are not the creator of it')
            raise redirect('/circles')

        for u in circle.users:
            u.__dict__['cid'] = circle_id
        wrappers = [u for u in circle.users if u.id != user.id]

        data = [util.to_datagrid(datagrid.circle_description_grid, wrappers, grid_display=len(wrappers)>0)]

        kw['cid']=circle_id
        widget.value = kw
        return dict(page='circles', name=circle.name, widget=widget, items=data, tooltip=t)

#    @expose()
#    @validate(circle_edit_form, error_handler=edit)
#    def put(self, *args, **kw):
#        user = handler.user.get_user_in_session(request)
#        circle_id = args[0]
#        circle = DBSession.query(Circle).filter(Circle.id == circle_id).first()
#        if not checker.user_own_circle(user.id, circle_id):
#            flash('you have no right to edit this circle : you are not the creator of it')
#            raise redirect('/circles')
#        handler.circle.edit(circle, kw['name'], kw['description'], user, kw['users'])
#        raise redirect('/circles')


    @require(has_permission('admin', msg='Only for admins'))
    @expose('pygdv.templates.list')
    def admin(self):
        c = DBSession.query(Circle).all()
        dc = [util.to_datagrid(circle_grid, c, "All circles", len(c)>0)]
        t = handler.help.tooltip['circle']
        return dict(page='circles', model='circle', tooltip=t, items=dc, value={})
    
     
