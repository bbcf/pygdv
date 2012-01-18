"""User Controller"""
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import not_anonymous, has_permission

from tg import expose, flash, require
from tg.controllers import redirect
from tg.decorators import paginate,with_trailing_slash

from pygdv.model import User
from pygdv.widgets.user import user_table, user_table_filler, user_new_form, user_edit_filler, user_edit_form
from pygdv.lib import constants
__all__ = ['UserController']


class UserController(CrudRestController):
    allow_only = has_permission(constants.perm_admin)
    model = User
    table = user_table
    table_filler = user_table_filler
    edit_form = user_edit_form
    new_form = user_new_form
    edit_filler = user_edit_filler


   
    
    @with_trailing_slash
    @expose('tgext.crud.templates.get_all')
    @expose('json')
    @paginate('value_list', items_per_page=3000)
    def get_all(self, *args, **kw):
        return CrudRestController.get_all(self, *args, **kw)

    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        flash("You haven't the right to delete any users")
        redirect('/users')
    
    
    
    @expose('tgext.crud.templates.edit')
    def edit(self, *args, **kw):
        flash("You haven't the right to edit any users")
        redirect('/users')
    
    
    
    @require(not_anonymous())
    @expose('genshi:tgext.crud.templates.new')
    def new(self, *args, **kw):
        flash("You haven't the right to add any users, this is the job of Tequila system")
        redirect('/users')
   
    @expose()
    @registered_validate(error_handler=new)
    def post(self, *args, **kw):
        pass
    
    
    @expose()
    @registered_validate(error_handler=edit)
    def put(self, *args, **kw):
        pass
    
