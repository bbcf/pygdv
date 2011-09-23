"""Permission Controller"""
from tgext.crud import CrudRestController

from repoze.what.predicates import has_permission

from tg import expose, flash
from tg.controllers import redirect
from tg import app_globals as gl

from pygdv.widgets.permission import perm_table, perm_table_filler, perm_new_form, perm_edit_filler, perm_edit_form
from pygdv.model import DBSession, Permission

class PermissionController(CrudRestController):
    allow_only = has_permission(gl.perm_admin)
    model = Permission
    table = perm_table
    table_filler = perm_table_filler
    edit_form = perm_edit_form
    new_form = perm_new_form
    edit_filler = perm_edit_filler


    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        for id in args :
            permission = DBSession.query(Permission).filter(Permission.id == id).first()
            if permission.name == gl.perm_admin:
                flash('Cannot delete admin permission')
                redirect('/permissions')
            if permission.name == gl.perm_user:
                flash('Cannot delete read permission')
                redirect('/permissions')
        return CrudRestController.post_delete(self, *args, **kw)
    
    
    @expose('tgext.crud.templates.edit')
    def edit(self, *args, **kw):
        pass