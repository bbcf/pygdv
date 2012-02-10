# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, request

from pygdv.lib.base import BaseController
from pygdv.model import DBSession, Project
from repoze.what.predicates import has_permission
from tg.controllers import redirect
from pygdv.lib import util
from pygdv.widgets.project import project_admin_grid


from pygdv.controllers import ErrorController, LoginController, GroupController
from pygdv.controllers import PermissionController, UserController, TrackController
from pygdv.controllers import SequenceController, ProjectController, CircleController
from pygdv.controllers import RightController, WorkerController, TaskController
from pygdv.controllers import InputController, DatabaseController, JobController
from pygdv.controllers import PublicController, HelpController

import pygdv

 
__all__ = ['RootController']


import inspect
from sqlalchemy.orm import class_mapper

models = {}
for m in pygdv.model.admin_models:
    m = getattr(pygdv.model, m)
    if not inspect.isclass(m):
        continue
    try:
        mapper = class_mapper(m)
        models[m.__name__.lower()] = m
    except:
        pass



class RootController(BaseController):
    """
    The root controller for the pygdv application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    
   
    error = ErrorController()
    login = LoginController()
   
    
    
    # admin controllers
    groups = GroupController(DBSession, menu_items=models)
    permissions = PermissionController(DBSession, menu_items=models)
    users = UserController(DBSession, menu_items=models)
    sequences = SequenceController(DBSession, menu_items=models)
    #rights = RightController(DBSession, menu_items=models)
    tasks = TaskController(DBSession, menu_items=models)
    inputs = InputController(DBSession, menu_items=models)
    
    # users controllers
    tracks = TrackController(DBSession)
    projects = ProjectController(DBSession)
    circles = CircleController(DBSession)
    jobs = JobController(DBSession)
    
    public = PublicController()
    # tasks controller
    workers = WorkerController()
   
    help = HelpController()
    
    # database controller
    database = DatabaseController()
    
    @expose('pygdv.templates.index')
    def index(self,*args,**kw):
        return dict(page='index')
    
    @expose('pygdv.templates.index')
    def login_needed(self):
        flash('You need to login', 'error')
        return dict(page='index')

    @expose('pygdv.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    
    @expose()
    def home(self,*args,**kw):
        raise redirect('/')
    
    
    
    
    ## DEVELOPMENT PAGES ##
    
    @require(has_permission('admin', msg='Only for admins'))
    @expose('pygdv.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(page='environ',environment=request.environ)

#    @require(has_permission('admin', msg='Only for admins'))
#    @expose('pygdv.templates.data')
#    @expose('json')
#    def data(self, **kw):
#        """This method showcases how you can use the same controller for a data page and a display page"""
#        return dict(page='data',params=kw)
    
    @expose('json')
    def test(self, x):
        from pygdv.celery import tasks
        res = tasks.test.delay((x))
        return dict(result=res.get())
    
    
    
    
    
    
    
