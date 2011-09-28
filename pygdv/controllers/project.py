"""Project Controller"""
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import not_anonymous, has_any_permission

from tg import expose, flash, require, request, tmpl_context, validate, url
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate, with_trailing_slash,without_trailing_slash

from pygdv.model import DBSession, Project, User
from pygdv.widgets.project import project_table, project_table_filler, project_new_form, project_edit_filler, project_edit_form, project_grid, project_sharing_grid
from pygdv import handler
from pygdv.lib import util
import os
import transaction

__all__ = ['ProjectController']


class ProjectController(CrudRestController):
    allow_only = has_any_permission(gl.perm_user, gl.perm_admin)
    model = Project
    table = project_table
    table_filler = project_table_filler
    edit_form = project_edit_form
    new_form = project_new_form
    edit_filler = project_edit_filler
    
    
   
    
    @with_trailing_slash
    @expose('pygdv.templates.list')
    @expose('json')
    #@paginate('items', items_per_page=10)
    def get_all(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        data = [util.to_datagrid(project_grid, user.projects, "Project Listing", len(user.projects)>0)]
        return dict(page='projects', model='project', form_title="new project",items=data,value=kw)
    
    @require(not_anonymous())
    @expose('pygdv.templates.form')
    def new(self, *args, **kw):
        print 'new'
        tmpl_context.widget = project_new_form
        user = handler.user.get_user_in_session(request)
        tmpl_context.tracks=user.tracks
        tmpl_context.circles=user.circles
        return dict(page='projects', value=kw, title='new Project')
    
    @expose()
    @validate(project_new_form, error_handler=new)
    def post(self, *args, **kw):
        print 'post'
        user = handler.user.get_user_in_session(request)
        '''
        create(name, sequence_id, user_id, tracks=None, isPublic=False, cicle_right):
        {'nr_assembly': u'70', 'name': None, 'species': u'2'}  
        
        '''
        handler.project.create(kw['name'], kw['nr_assembly'], user.id, tracks=kw['tracks'], circles=kw['circles'])
        transaction.commit()
        raise redirect('./') 
    
    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        print 'post_del'
        user = handler.user.get_user_in_session(request)
        id = args[0]
        for project in user.projects :
            if int(id) == project.id :
                return CrudRestController.post_delete(self, *args, **kw)
        flash("You haven't the right to delete any project which is not yours")
        raise redirect('./')
    
    
    @expose('pygdv.templates.form')
    def edit(self, *args, **kw):
        print 'edit'
        project = DBSession.query(Project).filter(Project.id == args[0]).first()
        tmpl_context.widget = project_edit_form
        tmpl_context.project = project
        kw['_method']='PUT'
        return dict(page='projects', value=kw, title='edit Project')
    
    @expose()
    @validate(project_edit_form, error_handler=edit)
    def put(self, *args, **kw):
        print 'put'
        print args
        print kw
        user = handler.user.get_user_in_session(request)
        id = args[0]
        for project in user.projects :
            if int(id) == project.id:
                handler.project.edit(project, kw['name'], kw['nr_assembly'], 
                                     user.id, tracks=kw['tracks'], circles=kw['circles'])
                raise redirect('../')
        flash("You haven't the right to edit any project which is not yours")
        raise redirect('../')
    
    
    @expose()
    def view(self, *args, **kw):
        return 'not implemented'


    
    @expose('pygdv.templates.list')
    def share(self, project_id, *args, **kw):
        if project_id is None:
            raise redirect('./')
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_project(user.id, 1):
            flash('You cannot share a project which is not yours')
            raise redirect('./')
        data = [util.to_datagrid(project_sharing_grid, project.circles_rights, "Project Sharing", len(project.circles_rights)>0)]
        return dict(page='projects', model='project', form_title="project sharing",items=data,value=kw)
       
    
    @expose()
    def post_share(self, project_id, circle_id, rights_checkboxes, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_project(user.id, 1):
             flash('You cannot modify a project which is not yours')   
             raise redirect('/')
        '''
        {'rights_checkboxes': [u'Read', u'Upload'], 'project_id': u'2', 'circle_id': u'1'}
        '''
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        circle_rights = DBSession.query(Project).filter()
        if not rights_checkboxes:
            
        #TODO change permissions
        raise redirect(url('/projects/share', {'project_id':project_id}))
                
       
    
    @expose()
    def test(self):
        from pygdv.lib import checker
        user = handler.user.get_user_in_session(request)
        print DBSession.query(Project).all()
        
        print checker.user_own_project(user.id, 1)
