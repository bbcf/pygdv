"""Group Controller"""
from tgext.crud import CrudRestController
from tg import expose, flash
from repoze.what.predicates import has_permission
from tg.controllers import redirect
from pygdv.widgets.group import group_table, group_table_filler, new_group_form, group_edit_filler, group_edit_form
from pygdv.model import DBSession, Group
from tg import app_globals as gl
__all__ = ['GroupController']


class GroupController(CrudRestController):
    allow_only = has_permission(gl.perm_admin)
    model = Group
    table = group_table
    table_filler = group_table_filler
    edit_form = group_edit_form
    new_form = new_group_form
    edit_filler = group_edit_filler


    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        for id in args :
            group = DBSession.query(Group).filter(Group.id == id).first()
            if group.name == gl.group_admins:
                flash('Cannot delete admin group')
                redirect('/groups')
            if group.name == gl.group_users:
                flash('Cannot delete users group')
                redirect('/groups')
        return CrudRestController.post_delete(self, *args, **kw)
    
    @expose('tgext.crud.templates.edit')
    def edit(self, *args, **kw):
        return CrudRestController.edit(self, *args, **kw)
    
    @expose()
    def put(self, *args, **kw):
        1/0
        CrudRestController.put(self, *args, **kw)