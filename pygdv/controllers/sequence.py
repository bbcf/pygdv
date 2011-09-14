"""Sequence Controller"""
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

    
