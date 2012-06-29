# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, request, url

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
from pygdv.controllers import PublicController, HelpController, GenRepController
from pygdv.controllers import SelectionController, PluginController, AdminController

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
   
    
    
    groups = GroupController(DBSession, menu_items=models)
    permissions = PermissionController(DBSession, menu_items=models)
    users = UserController(DBSession, menu_items=models)
    sequences = SequenceController(DBSession, menu_items=models)
    tasks = TaskController(DBSession, menu_items=models)
    inputs = InputController(DBSession, menu_items=models)
    tracks = TrackController()
    projects = ProjectController()
    circles = CircleController()
    jobs = JobController()
    public = PublicController()
    admin = AdminController()
    #workers = WorkerController()
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
    
    @expose('pygdv.templates.test')
    def test(self, **kw):
        print 'test %s' % kw
        from tg import url
        from pygdv.widgets import form
        w = form.TestForm(action=url('./test'))
        return dict(page='root', widget=w)
    

    @expose('pygdv.templates.koopa')
    def koopa(self, *args, **kw):
        from tw.api import js_callback
        colModel = [
                {'display' : 'ID', 'name' : 'id', 'width': 20, 'align' : 'center'},
                {'display' : 'ID2', 'name' : 'blou', 'width': 20, 'align' : 'center'},
        ]
        buttons = [{'name' : 'add', 'bclass' : 'add', 'onpress' : js_callback('add_record')},
                {'name' : 'del', 'bclass' : 'delete', 'onpress' : js_callback('delete_record')}]


        _id = 'test'
        from tg import url, tmpl_context
        fetchURL = url('/troopa')
        import tw.jquery as twjq
        grid = twjq.FlexiGrid(id=_id, buttons=buttons, fetchURL=fetchURL, colModel=colModel, title='koopa',
        useRp=True, rp=10, width=500, height=200, showTableToggleButton=True, usepager=True)
        data = [Koopa(i) for i in xrange(5)]
        tmpl_context.grid = grid

        return dict(page='koopa', data=data)

    @expose('pygdv.templates.peach')
    def peach(self, *args, **kw):
        import tw2.jqplugins.jqgrid as jq
        colNames = ['ID', 'SAME']
        colModel = [{'name' : 'blou', 'width' : 50, 'align' : 'center'},
        {'name' : 'blou'}]
        from tg import url
        opts = {'pager' : 'module-0-demo_pager', 'colNames' : colNames, 'colModel' : colModel, 'url' : url('/troopa')}
        pager_opts = {'refresh' : True}
        widget = jq.jqGridWidget(id='test', options=opts, pager_options=pager_opts).req()
        return dict(widget=widget, page='peach')

    @expose('json')
    def bowser(self, *args, **kw):
        print 'bowser %s, %s' % (args, kw)
        return {}

    @expose('json')
    def troopa(self, *args, **kw):
        print 'called troopa %s'% kw
        koopas = [Koopa(i) for i in xrange(5)]
        data = [{'id' : koopa.blou, 'cell' : [koopa.blou, koopa.blou]} for koopa in koopas]

        return dict(rows=data, total=5, counts=5)




import tw2.jqplugins.jqgrid as jq


class Koopa(object):
    def __init__(self, _id):
        self.blou = str(_id)

    def __repr__(self):
        return json.dumps(self.__dict__)