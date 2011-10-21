from tgext.crud import CrudRestController
from pygdv.widgets.input import input_table, input_table_filler, input_new_form, input_edit_filler, input_edit_form
from tg import app_globals as gl
from repoze.what.predicates import has_permission
from pygdv.model import Input, DBSession
from pygdv import handler
from tg import expose, flash, request
import shutil, os
from pygdv.lib.constants import json_directory

__all__ = ['InputController']


class InputController(CrudRestController):
    allow_only = has_permission(gl.perm_admin)
    model = Input
    table = input_table
    table_filler = input_table_filler
    edit_form = input_edit_form
    new_form = input_new_form
    edit_filler = input_edit_filler
    
    
    
    
    
    
    
    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        input = DBSession.query(Input).filter(Input.id == args[0]).first()
        try:
            os.remove(input.path)
            shutil.rmtree(os.path.join(json_directory(), input.sha1))
        except OSError :
            pass
        return CrudRestController.post_delete(self, *args, **kw)