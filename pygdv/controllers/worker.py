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
    
    
    
    def index(self, *args, **kw):
        print 'worker received : args : %s, kw : %s' % (args, kw)
        pass
    
    def new_selection(self, *args, **kw):
        pass
