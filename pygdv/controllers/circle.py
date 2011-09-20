"""Circle Controller"""
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import not_anonymous, has_permission

from tg import expose, flash, require, request, tmpl_context, validate
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate,with_trailing_slash, without_trailing_slash

from pygdv.model import DBSession, Circle, Species, User
from pygdv.widgets.circle import circle_table, circle_table_filler, circle_new_form, circle_edit_filler, circle_edit_form
from pygdv import handler
from pygdv.lib import util
from sqlalchemy import and_

import transaction

__all__ = ['CircleController']


class CircleController(CrudRestController):
    allow_only = has_permission(gl.perm_admin)
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
        return CrudRestController.get_all(self, *args, **kw)

    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        for id in args :
            circle = DBSession.query(Circle).filter(Circle.id == id).first()
            if user.id == circle.creator_id :
                return CrudRestController.post_delete(self, id)
        flash('you have no right to delete this circle : you are not the creator of it')
        raise redirect('./')                                      
    
    @expose('tgext.crud.templates.edit')
    def edit(self, *args, **kw):
        print 'edit'
        print args
        print kw
        user = handler.user.get_user_in_session(request)
        for id in args :
            circle = DBSession.query(Circle).filter(Circle.id == id).first()
            if user.id == circle.creator_id or DBSession.query(User).join(
                            Circle, User.circles).filter(
                            and_(Circle.id == id, User.id == user.id)).first() is not None :
                return CrudRestController.edit(self, id)
        flash('you have no right to edit this circle : you are not in the circle or you are not the creator of it')
        raise redirect('./')            
        #return CrudRestController.edit(self, *args, **kw)      
          
#          if circle.name == gl.perm_admin:
#              flash('Cannot delete admin permission')
#              redirect('/permissions')
#          if permission.name == gl.perm_user:
#              flash('Cannot delete read permission')
#              redirect('/permissions')
        #return CrudRestController.post_delete(self, *args, **kw)
    
    
#    
    
#    
#    
#    
#    @require(not_anonymous())
#    @expose('genshi:tgext.crud.templates.new')
#    def new(self, *args, **kw):
#        flash("You haven't the right to add any users, this is the job of Tequila system")
#        redirect('/users')
#   
#    @expose()
#    @registered_validate(error_handler=new)
#    def post(self, *args, **kw):
#        pass
#    
#    
#    @expose()
#    @registered_validate(error_handler=edit)
#    def put(self, *args, **kw):
#        pass
#    
    