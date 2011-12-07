"""Circle Controller"""
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import has_any_permission

from tg import expose, flash, require, request, tmpl_context, validate
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate,with_trailing_slash, without_trailing_slash

from pygdv.model import DBSession, Circle, Species, User
from pygdv.widgets.circle import circle_table, circle_table_filler, circle_new_form, circle_edit_filler, circle_edit_form
from pygdv import handler
from pygdv.lib import util, checker, constants
from sqlalchemy import and_


import transaction

__all__ = ['CircleController']


class CircleController(CrudRestController):
    allow_only = has_any_permission(constants.perm_admin, constants.perm_user)
    model = Circle
    table = circle_table
    table_filler = circle_table_filler
    edit_form = circle_edit_form
    new_form = circle_new_form
    edit_filler = circle_edit_filler

    @without_trailing_slash
    @expose('tgext.crud.templates.new')
    def new(self, *args, **kw):
        return CrudRestController.new(self, *args, **kw)
   
    @expose()
    @validate(circle_new_form, error_handler=new)
    def post(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        handler.circle.create(kw['name'], kw['description'], user.id, kw['users'])
        raise redirect('./') 
    
    
    @with_trailing_slash
    @expose('tgext.crud.templates.get_all')
    @expose('json')
    @paginate('value_list', items_per_page=7)
    def get_all(self, *args, **kw):
        kw['page']='circle'
        return CrudRestController.get_all(self, *args, **kw)

    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        circle_id = args[0]
        if not checker.user_own_circle(user.id, circle_id):
            flash('you have no right to delete this circle : you are not the creator of it')
            raise redirect('/circles') 
        return CrudRestController.post_delete(self, circle_id)
                                             
    
    @expose('tgext.crud.templates.edit')
    def edit(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        circle_id = args[0]
        if not checker.user_own_circle(user.id, circle_id):
            flash('you have no right to edit this circle : you are not the creator of it')
            raise redirect('/circles') 
        return CrudRestController.edit(self, circle_id)
    