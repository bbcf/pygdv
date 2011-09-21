"""Group Controller"""
from tgext.crud import CrudRestController
from tg import expose, flash
from repoze.what.predicates import has_permission
from tg.controllers import redirect
from pygdv.widgets.right import right_table, right_table_filler, right_new_form, right_edit_filler, right_edit_form
from pygdv.model import DBSession, Right
from tg import app_globals as gl
__all__ = ['RightController']


class RightController(CrudRestController):
    allow_only = has_permission(gl.perm_admin)
    model = Right
    table = right_table
    table_filler = right_table_filler
    edit_form = right_edit_form
    new_form = right_new_form
    edit_filler = right_edit_filler


    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
            
        return CrudRestController.post_delete(self, *args, **kw)
    
