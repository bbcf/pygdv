"""Project Controller"""
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import not_anonymous, has_any_permission

from tg import expose, flash, require, error, request, tmpl_context, validate, url
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate, with_trailing_slash,without_trailing_slash

from pygdv.model import DBSession, Project, User, RightCircleAssociation, Track, Job
from pygdv.widgets.project import project_table, project_with_right, project_table_filler, project_new_form, project_edit_filler, project_edit_form, project_grid,circles_available_form, tracks_available_form, project_sharing_grid, project_grid_sharing
from pygdv.widgets.track import track_in_project_grid
from pygdv.widgets import ModelWithRight
from pygdv import handler
from pygdv.lib import util
import os, json
import transaction
from pygdv.lib import checker
from pygdv.lib.jbrowse import util as jb
from pygdv.lib import constants
from sqlalchemy.sql import and_, or_, not_
import re

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
    @expose('pygdv.templates.project')
    @expose('json')
    #@paginate('items', items_per_page=10)
    def get_all(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        
        # user project
        user_projects = [util.to_datagrid(project_grid, user.projects, "Project Listing", len(user.projects)>0)]
        # shared projects
        project_with_rights = handler.project.get_shared_projects(user)
        
        if 'ordercol' in kw:
            util.order_data(kw['ordercol'], up)
        
        
        sp = []
        for project, rights in project_with_rights.iteritems():
            sp.append(ModelWithRight(project, {constants.right_read : constants.right_read in rights, 
                                               constants.right_download : constants.right_download in rights,
                                               constants.right_upload : constants.right_upload in rights}))
        
        shared_projects = [util.to_datagrid(project_with_right, sp, "Shared projects", len(sp)>0)]
        #TODO check with permissions
        
        return dict(page='projects', model='project', form_title="new project", user_projects=user_projects, shared_projects=shared_projects, value=kw)
    


    @require(not_anonymous())
    @expose('pygdv.templates.form')
    def new(self, *args, **kw):
        tmpl_context.widget = project_new_form
        user = handler.user.get_user_in_session(request)
        #tmpl_context.circles=user.circles
        return dict(page='projects', value=kw, title='new Project')

    @expose()
    @validate(project_new_form, error_handler=new)
    def post(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        handler.project.create(kw['name'], kw['nr_assembly'], user.id)
        transaction.commit()
        raise redirect('./')



    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        id = args[0]
        if not checker.check_permission_project(user.id, id, constants.right_upload_id):
            flash('You must have %s permission to view the project.' % constants.right_upload, 'error')
            raise redirect('./')
        return CrudRestController.post_delete(self, *args, **kw)



    @expose('pygdv.templates.project_detail')
    def detail(self, project_id):
        if project_id is None:
            raise redirect('./')
        user = handler.user.get_user_in_session(request)
        if not checker.check_permission_project(user.id, project_id, constants.right_download_id):
            flash('You must have %s permission to view the project.' % constants.right_download, 'error')
            raise redirect('./')

        # project info
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        data = util.to_datagrid(project_grid, [project])

        # track list
        track_list = [util.to_datagrid(track_in_project_grid, project.tracks, "Tracks associated", len(project.tracks)>0)]

        
        return dict(page='projects', model='Project', info=data,
                    track_list=track_list)


    @expose('pygdv.templates.form')
    def edit(self, project_id, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.check_permission_project(user.id, project_id, constants.right_upload_id):
            flash('You must have %s permission to view the project.' % constants.right_upload, 'error')
            raise redirect('/projects')

        project = DBSession.query(Project).filter(Project.id == project_id).first()
        tmpl_context.widget = project_edit_form
        tmpl_context.project = project
        tmpl_context.tracks = DBSession.query(Track).join(User.tracks).filter(
                            and_(User.id == user.id, Track.sequence_id == project.sequence_id)).all()

        kw['_method']='PUT'
        return dict(page='projects', value=kw, title='edit Project')

    @expose()
    @validate(project_edit_form, error_handler=edit)
    def put(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        print kw
        project_id = args[0]
        if not checker.check_permission_project(user.id, project_id, constants.right_upload_id):
            flash('You must have %s permission to view the project.' % constants.right_upload, 'error')
            raise redirect('/projects')
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        handler.project.edit(project, kw['name'],
                                     user.id, tracks=kw['tracks'])
        raise redirect('/projects')








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
        cr_data = [util.to_datagrid(project_sharing_grid, project.circles_rights, "Sharing", len(project.circles_rights)>0)]

        kw['project_id'] = project_id
        return dict(page='projects', model='Project', info=data,
                    circle_right_data=cr_data, form_title='Circles availables', value=kw)


    @expose()
    def post_share(self, project_id, circle_id, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_project(user.id, project_id):
            flash('You cannot modify a project which is not yours')
            raise redirect(url('/'))
        
        print '[x] post_share [x] project_id %s, circle_id %s, args : %s, kw : %s' % (project_id, circle_id, args, kw)
        
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
            raise redirect(url('/'))
        print 'ddfddffd'
        print args
        print kw
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        if 'circles' in kw:
            if isinstance(kw['circles'], list):
                handler.project.add_read_right_to_circles_ids(project, kw['circles'])
            else :
                handler.project.add_read_right(project, kw['circles'])
        raise redirect(url('/projects/share', {'project_id':project_id}))

    @expose()
    def test(self, n):
        user = handler.user.get_user_in_session(request)
        p = handler.project.get_projects_with_permission(user.id, n)
        print p
        raise redirect('./');

    @expose('pygdv.templates.add_track')
    def add_track(self, project_id, *args, **kw):
        # project info
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        data = util.to_datagrid(project_grid, [project])
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_project(user.id, project_id):
            flash('You cannot modify a project which is not yours')
            raise redirect(url('/'))
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
            raise redirect(url('/'))
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        if not isinstance(tracks,list):
                handler.project.add_tracks(project,[tracks])
        else :
            handler.project.add_tracks(project,tracks)
        raise redirect(url('/projects/add_track', {'project_id':project_id}))






    @expose('pygdv.templates.view')
    def view(self, project_id, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.check_permission_project(user.id, project_id, constants.right_read_id):
            flash('You must have %s permission to view the project.' % constants.right_read, 'error')
            raise redirect(url('/'))
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        tracks = project.tracks
        refSeqs = 'refSeqs = %s' % json.dumps(jb.ref_seqs(project.sequence_id))
        
        trackInfo = 'trackInfo = %s' % json.dumps(jb.track_info(tracks))
        parameters = 'var b = new Browser(%s)' % jb.browser_parameters(
                        constants.DATA_ROOT, constants.STYLE_ROOT, constants.IMAGE_ROOT, ','.join([track.name for track in tracks]))
        
        style_control = '''function getFeatureStyle(type, div){
        div.style.backgroundColor='#3333D7';div.className='basic';
        switch(type){
        %s
        }};
        ''' % jb.features_style(tracks)
        
        control = 'b.showTracks();initGDV(b, %s)' % project.id
        
        jobs = DBSession.query(Job).filter(and_(Job.project_id == project.id, not_(Job.output == constants.job_output_reload))).all()
        
        jobs_output = [{'job_id' : job.id, 
                       'status' : job.status, 
                       'job_name' : job.name,
                       'job_description' : job.description,
                       'output' : job.output, 
                       'error' : job.traceback}
                      for job in jobs
                      ]
        
        return dict(species_name=project.species.name, 
                    nr_assembly_id=project.sequence_id, 
                    project_id=project.id,
                    is_admin=True,
                    init_jobs=json.dumps(jobs_output),
                    ref_seqs = refSeqs,
                    track_info = trackInfo,
                    parameters = parameters,
                    style_control = style_control,
                    control = control,
                    page='view')
    
    
    
