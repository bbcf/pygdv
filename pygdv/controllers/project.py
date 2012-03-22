"""Project Controller"""
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import not_anonymous, has_any_permission, has_permission

from tg import expose, flash, require, error, request, tmpl_context, validate, url
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate, with_trailing_slash, without_trailing_slash
import tg

from pygdv.model import DBSession, Project, User, RightCircleAssociation, Track, Job
from pygdv.widgets.project import project_table,  project_admin_grid, project_with_right, project_table_filler, project_new_form, project_edit_filler, project_edit_form, project_grid,circles_available_form, tracks_available_form, project_sharing_grid, project_grid_sharing
from pygdv.widgets.track import track_in_project_grid
from pygdv.widgets import ModelWithRight
from pygdv import handler
from pygdv.lib import util
import os, json
import transaction
from pygdv.lib import checker
from pygdv.lib.jbrowse import util as jb
from pygdv.lib import constants, reply

from sqlalchemy.sql import and_, or_, not_
import re

__all__ = ['ProjectController']


class ProjectController(CrudRestController):
    allow_only = has_any_permission(constants.perm_user, constants.perm_admin)
    model = Project
    table = project_table
    table_filler = project_table_filler
    edit_form = project_edit_form
    new_form = project_new_form
    edit_filler = project_edit_filler

    
    @with_trailing_slash
    @expose('json')
    def get(self, project_key, **kw):
        project = DBSession.query(Project).filter(Project.key == project_key).first()
        if project is None:
            return reply.error(request, 'Wrong key', './', {})
        user = handler.user.get_user_in_session(request)
        if not checker.check_permission_project(user.id, project.id, constants.right_upload_id):
            return reply.error(request, 'Wrong key', './', {})
        else :
            return reply.normal(request, 'You can upload track on this project', './', {'project' : project})
        
        
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
        
        
        
        sp = []
        for project, rights in project_with_rights.iteritems():
            sp.append(ModelWithRight(project, {constants.right_read : constants.right_read in rights, 
                                               constants.right_download : constants.right_download in rights,
                                               constants.right_upload : constants.right_upload in rights}))
        shared_projects = [util.to_datagrid(project_with_right, sp, "Shared projects", len(sp)>0)]
        #TODO check with permissions
        
        control = '''
       
        '''
        return dict(page='projects', model='project',form_title="New project", user_projects=user_projects, shared_projects=shared_projects, control=control, value=kw)
    


    @require(not_anonymous())
    @expose('pygdv.templates.form')
    def new(self, *args, **kw):
        tmpl_context.widget = project_new_form
        user = handler.user.get_user_in_session(request)
        #tmpl_context.circles=user.circles
        return dict(page='projects', value=kw, title='New Project')
    
    @expose('json')
    def create(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not 'name' in kw:
            return reply.error(request, 'Missing project `name`.', './', {})
        
        if not 'assembly' in kw:
            return reply.error(request, 'Missing project `assembly` identifier.', './', {})
            
        project = handler.project.create(kw['name'], kw['assembly'], user.id)
        return reply.normal(request, 'Project successfully created.', './', {'project' : project})  
    
    @expose()
    @validate(project_new_form, error_handler=new)
    def post(self, *args, **kw):
        
        return self.create(*args, **kw)

    

    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        project_id = args[0]
        if not checker.check_permission_project(user.id, project_id, constants.right_upload_id):
            flash('You must have %s permission to delete the project.' % constants.right_upload, 'error')
            raise redirect('./')
        handler.project.remove_sharing(project_id)
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

        
        return dict(page='projects', model='Project detail', info=data,
                    track_list=track_list)


    @expose('pygdv.templates.form')
    def edit(self, project_id, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.check_permission_project(user.id, project_id, constants.right_upload_id):
            flash('You must have %s permission to view the project.' % constants.right_upload, 'error')
            raise redirect('/projects')

        project = DBSession.query(Project).filter(Project.id == project_id).first()
        tmpl_context.widget = project_edit_form
        project_tracks = project.tracks
        tmpl_context.selected_tracks =  project_tracks
        tmpl_context.project = project
        user_tracks = DBSession.query(Track).join(User.tracks).filter(
                            and_(User.id == user.id, Track.sequence_id == project.sequence_id,
                            not_(Track.id.in_([t.id for t in project_tracks])))
                                 ).all()
        
        tmpl_context.tracks = user_tracks
        
        kw['_method']='PUT'
        return dict(page='projects', value=kw, title='Edit Project')

    @expose()
    @validate(project_edit_form, error_handler=edit)
    def put(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        project_id = args[0]
        if not checker.check_permission_project(user.id, project_id, constants.right_upload_id):
            flash('You must have %s permission to edit the project.' % constants.right_upload, 'error')
            raise redirect('/projects')
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        handler.project.edit(project, kw['name'],
                                     project.user_id, tracks=kw['tracks'])
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
        
        # public url
        pub = url('/public/project', {'id' : project_id, 'k' : project.key})
       
        # download url
        print project.download_key
        if project.download_key is None:
            project.download_key = project.setdefaultkey()
        
        down = url('/public/project', {'id' : project_id, 'k' : project.download_key})
       
        kw['project_id'] = project_id
        return dict(page='projects', model='Project', info=data,
                    circle_right_data=cr_data, form_title='Circles availables', value=kw, public=pub, download=down)


    @expose()
    def post_share(self, project_id, circle_id, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_project(user.id, project_id):
            flash('You cannot modify a project which is not yours')
            raise redirect(url('/'))
        
        
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
        
#        if not GenRep().is_up():
#            raise redirect(url('/error', {'m': 'Genrep service is down. Please try again later.'}))
        
        
        user = handler.user.get_user_in_session(request)
        if not checker.check_permission_project(user.id, project_id, constants.right_read_id):
            flash('You must have %s permission to view the project.' % constants.right_read, 'error')
            raise redirect(url('/'))

        # get the project
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        tracks = project.tracks
        
        seq = project.sequence
        default_tracks = seq.default_tracks
        all_tracks = tracks + default_tracks
        
        # test if all track names are differents
        trackNames = []
        for t in all_tracks:
            while t.name in trackNames:
                ind = 0
                while(t.name[-(ind + 1)].isdigit()):
                    ind += 1
                cpt = t.name[-ind:]
                try : 
                    cpt = int(cpt)
                except ValueError:
                    cpt = 0
                cpt += 1
                
                tmp_name = t.name
                if ind > 0:
                    tmp_name = t.name[:-ind]
                t.name = tmp_name + str(cpt)
            
            t.accessed
            DBSession.add(t)
            DBSession.flush()
            trackNames.append(t.name)
        
        # prepare some different parameters
        refSeqs = 'refSeqs = %s' % json.dumps(jb.ref_seqs(project.sequence_id))
        
        trackInfo = 'trackInfo = %s' % json.dumps(jb.track_info(all_tracks, assembly_id=project.sequence_id))
        parameters = 'var b = new Browser(%s)' % jb.browser_parameters(
                        constants.data_root(), constants.style_root(), constants.image_root(), ','.join([track.name for track in all_tracks]))
        
        style_control = '''function getFeatureStyle(type, div){
        div.style.backgroundColor='#3333D7';div.className='basic';
        switch(type){
        %s
        }};
        ''' % jb.features_style(all_tracks)
        
        
        selections = 'init_locations = %s' % handler.selection.selections(project_id)
        
        # prepare _gdv_info
        info = {}
        prefix = tg.config.get('prefix')
        if prefix : info['prefix'] = prefix
        info['sequence_id'] = project.sequence_id
        info['admin'] = True
        info = json.dumps(info)

        control = 'b.showTracks();initGDV(b, %s, %s);' % (project.id, info)
        
        
        if 'loc' in kw:
            control += 'b.navigateTo("%s");' % kw['loc']
        
        # get jobs
        jobs = 'init_jobs = %s' % handler.job.jobs(project_id)
        
        # get operations 
        operations_path = 'init_operations = %s' % json.dumps(handler.plugin.get_operations_paths(), default=handler.plugin.encode_tree)
        
        return dict(species_name=project.species.name, 
                    nr_assembly_id=project.sequence_id, 
                    project_id=project.id,
                    is_admin=True,
                    ref_seqs = refSeqs,
                    track_info = trackInfo,
                    parameters = parameters,
                    style_control = style_control,
                    control = control,
                    selections = selections,
                    operations_path = operations_path,
                    jobs = jobs,
                    page = 'view')
    
    @expose()
    def copy(self, project_id, **kw):
        user = handler.user.get_user_in_session(request)
        if 'k' in kw:
            project = DBSession.query(Project).filter(Project.id == project_id).first()
            if not kw['k'] == project.download_key:
                return reply.error(request, 'You have no right to copy this project in your profile.', './', {})
        elif not checker.check_permission_project(user.id, project_id, constants.right_download_id):
            return reply.error(request, 'You have no right to copy this project in your profile.', './', {})
        handler.project.copy(user.id, project_id)
        return reply.normal(request, 'Copy successfull', '/projects', {})
        
        
        
    @require(has_permission('admin', msg='Only for admins'))
    @expose('pygdv.templates.admin_project')
    def admin(self):
        projects = DBSession.query(Project).all()
        data_projects = [util.to_datagrid(project_admin_grid, projects, "All projects", len(projects)>0)]
        return dict(page='projects', model='project',form_title="new project", projects=data_projects, value={})
