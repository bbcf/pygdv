from tgext.crud import CrudRestController
from pygdv.widgets.input import input_table, input_table_filler, input_new_form, input_edit_filler, input_edit_form
from repoze.what.predicates import has_permission
from pygdv.model import Input, DBSession
from pygdv import handler
from tg import expose, flash, request
import shutil, os
from tg.decorators import with_trailing_slash, paginate
from pygdv.lib.constants import json_directory
from pygdv.lib import constants

__all__ = ['InputController']


class InputController(CrudRestController):
    allow_only = has_permission(constants.perm_admin)
    model = Input
    table = input_table
    table_filler = input_table_filler
    edit_form = input_edit_form
    new_form = input_new_form
    edit_filler = input_edit_filler
    
    
    
    
    @with_trailing_slash
    @expose('tgext.crud.templates.get_all')
    @expose('json')
    @paginate('value_list', items_per_page=1000)
    def get_all(self, *args, **kw):
        return CrudRestController.get_all(self, *args, **kw)
    
    
    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        input = DBSession.query(Input).filter(Input.id == args[0]).first()
        try:
            os.remove(input.path)
            shutil.rmtree(os.path.join(json_directory(), input.sha1))
        except OSError :
            pass
        return CrudRestController.post_delete(self, *args, **kw)