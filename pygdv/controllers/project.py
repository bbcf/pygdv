"""Project Controller"""
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import not_anonymous, has_any_permission

from tg import expose, flash, require, request, tmpl_context, validate
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate, with_trailing_slash,without_trailing_slash

from pygdv.model import DBSession, Project
from pygdv.widgets.project import project_table, project_table_filler, project_new_form,NewProjectFrom, project_edit_filler, project_edit_form, project_grid
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
        data = [util.to_datagrid(project_grid, user.projects, "Project list", len(user.projects)>0)]
        return dict(page='projects', model='project', form_title="new project",items=data,value=kw)
    
    @require(not_anonymous())
    @expose('pygdv.templates.form')
    def new(self, *args, **kw):
        tmpl_context.widget = project_new_form
        user = handler.user.get_user_in_session(request)
        tmpl_context.tracks=user.tracks
        tmpl_context.circle_rights=user.circles
        return dict(page='projects', value=kw, title='new Project')
    
    @expose()
    @validate(project_new_form, error_handler=new)
    def post(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        '''
        create(name, sequence_id, user_id, tracks=None, isPublic=False, cicle_right):
        {'nr_assembly': u'70', 'name': None, 'species': u'2'}  
        
        '''
        handler.project.create(kw['name'], kw['nr_assembly'], user.id, tracks=kw['tracks'])
        print args
        print kw
        raise redirect('./') 
    
#    @require(not_anonymous())
#    @expose('pygdv.templates.form')
#    def new(self, *args, **kw):
#        tmpl_context.widget = project_new_form
#        return dict(page='projects', value=kw, title='new Track')
#    
#    
#
#    @expose('genshi:tgext.crud.templates.post_delete')
#    def post_delete(self, *args, **kw):
#        user = handler.user.get_user_in_session(request)
#        id = args[0]
#        for project in user.projects :
#            if int(id) == project.id :
#                return CrudRestController.post_delete(self, *args, **kw)
#        flash("You haven't the right to delete any projects which is not yours")
#        raise redirect('./')
#    
#    
#    
#    @expose('tgext.crud.templates.edit')
#    def edit(self, *args, **kw):
#        flash("You haven't the right to edit any projects")
#        raise redirect('./')
#    
#    
#    
#  
#   
#    @expose()
#    @validate(project_new_form, error_handler=new)
#    def post(self, *args, **kw):
#        user = handler.user.get_user_in_session(request)
#        files = util.upload(**kw)
#        if files is not None:
#            for filename, file in files:
#                handler.project.create_project(user.id, file=file, projectname=filename)
#            transaction.commit()
#            flash("Track(s) successfully uploaded.")
#        else :
#            flash("No file to upload.")
#        raise redirect('./') 
#        
#    
##    @with_trailing_slash
##    @expose('tgext.crud.templates.get_all')
##    @expose('json')
##    @paginate('value_list', items_per_page=7)
##    def get_all(self, *args, **kw):
##        return CrudRestController.get_all(self, *args, **kw)
#
#   
#  
#    
#    
#    @expose()
#    @registered_validate(error_handler=edit)
#    def put(self, *args, **kw):
#        pass
        