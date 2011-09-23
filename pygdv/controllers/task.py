"""Tasks Controller"""
from tgext.crud import CrudRestController
from tg import expose, flash
from repoze.what.predicates import has_permission
from tg.controllers import redirect
from pygdv.widgets.tasks import celerytask_table, celerytask_table_filler, celerytask_new_form, celerytask_edit_filler, celerytask_edit_form
from pygdv.model import DBSession, CeleryTask
from tg import app_globals as gl
__all__ = ['TaskController']


class TaskController(CrudRestController):
    allow_only = has_permission(gl.perm_admin)
    model = CeleryTask
    table = celerytask_table
    table_filler = celerytask_table_filler
    edit_form = celerytask_edit_form
    new_form = celerytask_new_form
    edit_filler = celerytask_edit_filler
