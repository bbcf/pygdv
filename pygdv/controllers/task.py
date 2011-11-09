"""Tasks Controller"""
from tgext.crud import CrudRestController
from tg import expose, flash, request
from repoze.what.predicates import has_permission
from tg.decorators import with_trailing_slash, paginate
from tg.controllers import redirect
from pygdv.widgets.tasks import celerytask_table, celerytask_table_filler, celerytask_new_form, celerytask_edit_filler, celerytask_edit_form, task_grid
from pygdv.model import DBSession, Task
from tg import app_globals as gl
from pygdv import handler
from pygdv.lib import util
from celery.result import AsyncResult
__all__ = ['TaskController']


class TaskController(CrudRestController):
    allow_only = has_permission(gl.perm_admin)
    model = Task
    table = celerytask_table
    table_filler = celerytask_table_filler
    edit_form = celerytask_edit_form
    new_form = celerytask_new_form
    edit_filler = celerytask_edit_filler


    @with_trailing_slash
    @expose('pygdv.templates.list')
    @paginate('items', items_per_page=10)
    @expose('json')
    def get_all(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        tasks = DBSession.query(Task).all()
        data = [util.to_datagrid(task_grid, tasks, "Task Listing", len(tasks)>0)]
        return dict(page='tasks', model='task', form_title="new task",items=data,value=kw)
    
    
    @expose()
    def get_result(self, id):
        user = handler.user.get_user_in_session(request)
        task = DBSession.query(Task).filter(Task.id == id).first()
        result = AsyncResult(task.task_id)
        if not result.ready():
            return 'result not ready'
        if not result.successful():
            return 'task ended with error'
        return '%s' % result.get()
        
