from pygdv.lib.base import BaseController
from tg import expose
from repoze.what.predicates import has_permission
from tg import app_globals as gl
from pygdv.celery import tasks
from celery.task import chord
from symbol import except_clause

__all__ = ['WorkerController']



class WorkerController(BaseController):
    #allow_only = has_permission(gl.perm_admin)
    
    
    @expose('json')
    def add(self, x, y, *args, **kw):
        t = tasks.add.delay(x,y)
        return 'task launched'
    
    @expose('json')
    def a(self):
        t = tasks.hellochord.delay()
        return 'task launched'
    
    
    @expose('json')
    def b(self):
        t = tasks.hellotakset().delay()
        return 'task launched'