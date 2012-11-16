# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, request, url

from pygdv.lib.base import BaseController
from pygdv.model import DBSession
from repoze.what.predicates import has_permission, has_any_permission
from tg.controllers import redirect


from pygdv.controllers import ErrorController, LoginController
from pygdv.controllers import TrackController
from pygdv.controllers import  ProjectController, CircleController
from pygdv.controllers import  SequenceController
from pygdv.controllers import  DatabaseController, JobController
from pygdv.controllers import PublicController, HelpController, GenRepController
from pygdv.controllers import SelectionController, PluginController

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
   
    
    
    sequences = SequenceController()
    tracks = TrackController()
    projects = ProjectController()
    circles = CircleController()
    jobs = JobController()
    public = PublicController()
    help = HelpController()
    genrep = GenRepController()
    database = DatabaseController()
    selections = SelectionController()
    plugins = PluginController()
    
    @expose('pygdv.templates.index')
    def index(self,*args,**kw):
        raise redirect('/tracks')
    
    @expose('pygdv.templates.help')
    def login_needed(self):
        flash('You need to login', 'error')
        return dict(page='index')

    
    #@require(has_permission('admin', msg='Only for admins'))
    @expose()
    def test_files(self, id):
        import os
        from pkg_resources import resource_filename
        from pygdv.tests.test_input_files import samples
        from tg import response
        samples_path = resource_filename('pygdv.tests', 'test_files')
        print samples[int(id)]

        _f = open(os.path.join(samples_path, samples[int(id)]))
        response.content_type = 'plain/text'
        response.headerlist.append(('Content-Disposition', 'attachment;filename=%s' % samples[int(id)]))
        return _f.read()

    @expose('pygdv.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    
    @expose()
    def home(self, *args, **kw):
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

    @require(has_any_permission('admin', 'user', msg='You must be logged'))
    @expose()
    def private_key(self):
        from pygdv import handler
        user = handler.user.get_user_in_session(request)
        return user.key

