"""Project Controller"""
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import not_anonymous, has_any_permission

from tg import expose, flash, require, request, tmpl_context, validate, url
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate, with_trailing_slash,without_trailing_slash

from pygdv.model import DBSession, Project, User, RightCircleAssociation
from pygdv.widgets.project import project_table, project_table_filler, project_new_form, project_edit_filler, project_edit_form, project_grid,circles_available_form, tracks_available_form, project_sharing_grid
from pygdv import handler
from pygdv.lib import util
import os
import transaction
from pygdv.lib import checker

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

        # user project
        data = [util.to_datagrid(project_grid, user.projects, "Project Listing", len(user.projects)>0)]

        # shared projects
        #TODO check with permissions

        return dict(page='projects', model='project', form_title="new project",items=data,value=kw)



    @require(not_anonymous())
    @expose('pygdv.templates.form')
    def new(self, *args, **kw):
        print 'new'
        tmpl_context.widget = project_new_form
        user = handler.user.get_user_in_session(request)
        tmpl_context.tracks=user.tracks
        #tmpl_context.circles=user.circles
        return dict(page='projects', value=kw, title='new Project')

    @expose()
    @validate(project_new_form, error_handler=new)
    def post(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        handler.project.create(kw['name'], kw['nr_assembly'], user.id, tracks=kw['tracks'])
        transaction.commit()
        raise redirect('./')





    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        id = args[0]
        if not checker.user_own_project(user.id, id):
            flash("You haven't the right to delete any project which is not yours")
            raise redirect('./')
        return CrudRestController.post_delete(self, *args, **kw)








    @expose('pygdv.templates.form')
    def edit(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        project_id = args[0]
        if not checker.user_own_project(user.id, project_id):
            flash("You haven't the right to edit any project which is not yours")
            raise redirect('/projects')

        project = DBSession.query(Project).filter(Project.id == project_id).first()
        tmpl_context.widget = project_edit_form
        tmpl_context.project = project
        tmpl_context.tracks=user.tracks
        #tmpl_context.circles=user.circles

        kw['_method']='PUT'
        return dict(page='projects', value=kw, title='edit Project')

    @expose()
    @validate(project_edit_form, error_handler=edit)
    def put(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        id = args[0]
        for project in user.projects :
            if int(id) == project.id:
                handler.project.edit(project, kw['name'], kw['nr_assembly'],
                                     user.id, tracks=kw['tracks'])
                raise redirect('../')
        flash("You haven't the right to edit any project which is not yours")
        raise redirect('../')







    @expose()
    def view(self, *args, **kw):
        return 'not implemented'



    @expose('pygdv.templates.project_sharing')
    def share(self, project_id, *args, **kw):
        if project_id is None:
            raise redirect('./')
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_project(user.id, project_id):
            flash('You cannot share a project which is not yours')
            raise redirect('./')

        # project info
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        data = util.to_datagrid(project_grid, [project])

        # circles available
        tmpl_context.widget = circles_available_form
        tmpl_context.circles = user.circles

        # circles with rights
        cr_data = [util.to_datagrid(project_sharing_grid, project.circles_rights, "sharing", len(project.circles_rights)>0)]

        kw['project_id'] = project_id
        return dict(page='projects', model='Project', info=data,
                    circle_right_data=cr_data, form_title='Circles availables', value=kw)


    @expose()
    def post_share(self, project_id, circle_id, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_project(user.id, project_id):
             flash('You cannot modify a project which is not yours')
             raise redirect('/')
        if 'rights_checkboxes' in kw:
            rights_checkboxes = kw['rights_checkboxes']
            if not isinstance(rights_checkboxes,list):
                rights = []
                rights.append(rights_checkboxes)
            else :
                rights = rights_checkboxes
            handler.project.change_rights(project_id, circle_id, rights)

        else :
            handler.project.change_rights(project_id, circle_id)
        raise redirect(url('/projects/share', {'project_id':project_id}))

    @expose()
    def post_share_add(self,project_id, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_project(user.id, project_id):
             flash('You cannot modify a project which is not yours')
             raise redirect('/')
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        if 'circles' in kw:
            if isinstance(kw['circles'], list):
                handler.project.add_read_right_to_circles_ids(project, kw['circles'])
            else :
                handler.project.add_read_right(project, kw['circles'])
        raise redirect(url('/projects/share', {'project_id':project_id}))

    @expose()
    def test(self):

        user = handler.user.get_user_in_session(request)
        print DBSession.query(Project).all()

        print checker.user_own_project(user.id, 1)


    @expose('pygdv.templates.add_track')
    def add_track(self, project_id, *args, **kw):
        # project info
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        data = util.to_datagrid(project_grid, [project])
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_project(user.id, project_id):
             flash('You cannot modify a project which is not yours')
             raise redirect('/')
        tmpl_context.widget = tracks_available_form
        tmpl_context.tracks = user.tracks
        kw['project_id'] = project_id
        return dict(page='projects', model='Project', info=data, form_title='Add track(s)',
                    value=kw)

    @expose()
    def add(self, project_id, tracks, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_project(user.id, project_id):
             flash('You cannot modify a project which is not yours')
             raise redirect('/')
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        if not isinstance(tracks,list):
                handler.project.add_tracks(project,[tracks])
        else :
             handler.project.add_tracks(project,tracks)
        raise redirect(url('/projects/add_track', {'project_id':project_id}))


