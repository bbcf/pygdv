"""Project Controller"""
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import not_anonymous, has_any_permission, has_permission
from pygdv.lib.base import BaseController
from tg import expose, flash, require, error, request, tmpl_context, validate, url
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate, with_trailing_slash, without_trailing_slash
import tg
from pygdv.widgets import datagrid

from pygdv.model import DBSession, Project, User, RightCircleAssociation, Track, Job, Sequence
from pygdv.widgets.project import project_table,  project_admin_grid, project_with_right, project_table_filler, project_new_form, project_edit_filler, project_edit_form, project_grid,circles_available_form, tracks_available_form, project_sharing_grid, project_grid_sharing
from pygdv.widgets.track import track_in_project_grid
from pygdv.widgets import ModelWithRight
from pygdv import handler
from pygdv.lib import util, plugin
import os, json, urllib2
from pygdv.widgets import form
import transaction
from pygdv.lib import checker
from pygdv.lib.jbrowse import util as jb
from pygdv.lib import constants, reply
import tw2.core as twc
from sqlalchemy.sql import and_, or_, not_
import re

__all__ = ['ProjectController']


class ProjectController(BaseController):
    allow_only = has_any_permission(constants.perm_user, constants.perm_admin)


    @expose('pygdv.templates.project_new')
    def new(self, *args, **kw):
        tmpl_context.widget = project_new_form
        user = handler.user.get_user_in_session(request)
        #tmpl_context.circles=user.circles
        return dict(page='projects', value=kw, model='project')


    @with_trailing_slash
    @expose('pygdv.templates.project_edit')
    def edit(self, *args, **kw):
        user = handler.user.get_user_in_session(request)

        if request.method == 'GET':
            project_id = args[0]
        else :
            project_id = kw.get('pid')

        if not checker.check_permission(user=user, project_id=project_id, right_id=constants.right_upload_id):
            flash('You must have %s permission to edit the project.' % constants.right_upload, 'error')
            raise redirect('/tracks/', {'pid' : project_id})


        widget = form.EditProject(action=url('/projects/edit/%s' % project_id)).req()
        widget.value = {'pid' : project_id}
        project = DBSession.query(Project).filter(Project.id == project_id).first()

        tracks = DBSession.query(Track).join(User.tracks).filter(
            and_(User.id == user.id, Track.sequence_id == project.sequence_id,
                not_(Track.id.in_([t.id for t in project.tracks])))
        ).all()


        if request.method == 'GET':
            widget.child.children[1].value = project.name
            widget.child.children[2].options = [('','')] + [(t.id, t.name) for t in tracks] + [(t.id, t.name, {'selected' : True}) for t in project.tracks]
            return dict(page='tracks', widget=widget, project_id=project_id)

        try:
            widget.validate(kw)
        except twc.ValidationError as e:
            w = e.widget
            w.child.children[1].value = project.name
            w.child.children[2].options = [(t.id, t.name) for t in tracks] + [(t.id, t.name, {'selected' : True}) for t in project.tracks]
            return dict(page='tracks', widget=w, project_id=project_id)
        track_ids = kw.get('tracks', [])
        if not track_ids: track_ids = []
        if not isinstance(track_ids, list):
            track_ids = [track_ids]
        if len(track_ids) > 0 and '' in track_ids: track_ids.remove('')
        handler.project.e(project_id=project_id, name=kw.get('name'), track_ids=track_ids)

        raise redirect('/tracks/', {'pid' : project_id})







    
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
        
        
    #@paginate('items', items_per_page=10)
    def index(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        
        # user project
        user_projects = [util.to_datagrid(datagrid.project_grid, user.projects, "Project Listing", len(user.projects)>0)]
        # shared projects
#        project_with_rights = handler.project.get_shared_projects(user)
#
#        sp = []
#        for project, rights in project_with_rights.iteritems():
#            sp.append(ModelWithRight(project, {constants.right_read : constants.right_read in rights,
#                                               constants.right_download : constants.right_download in rights,
#                                               constants.right_upload : constants.right_upload in rights}))
#        shared_projects = [util.to_datagrid(project_with_right, sp, "Shared projects", len(sp)>0)]
        #TODO check with permissions
        
        control = '''
       
        '''
        t = handler.help.tooltip['project']
        return dict(page='projects', model='project',form_title="New project", items=user_projects, value=kw, tooltip=t)
    




    @expose('json')
    def create(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not 'name' in kw:
            return reply.error(request, 'Missing project `name`.', './', {})
        
        if not 'assembly' in kw:
            return reply.error(request, 'Missing project `assembly` identifier.', './', {})

        sequence = DBSession.query(Sequence).filter(Sequence.id == int(kw.get('assembly'))).first()
        if sequence is None:
            return reply.error(request, "Assembly doesn't exist in GDV.", './', {})

        project = handler.project.create(kw['name'], kw['assembly'], user.id)
        return reply.normal(request, 'Project successfully created.', '/tracks', {'project' : project})  
    
    @expose()
    @validate(project_new_form, error_handler=new)
    def post(self, *args, **kw):
        return self.create(*args, **kw)


    @expose('json')
    def delete(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if len(args) > 0:
            project_id = args[0]
            if not checker.check_permission(user=user, project_id=project_id, right_id=constants.right_upload_id):
                return reply.error(request, "You must have %s permission to delete the project." % constants.right_upload,
                        '/tracks', {'error' : 'wrong credentials'})

        handler.project.delete(project_id=project_id)
        return reply.normal(request, 'Project successfully deleted.', '/tracks', {'success' : 'project deleted'})


    def post_delete(self, *args, **kw):
        user = handler.user.get_user_in_session(request)

        project_id = kw.get('id', None)

        if project_id is not None:
            if not checker.check_permission_project(user.id, project_id, constants.right_upload_id):
                flash('You must have %s permission to delete the project.' % constants.right_upload, 'error')
                raise redirect('./')
        handler.project.delete(project_id=project_id)
        raise redirect('./')




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
    def share(self, *args, **kw):
        user = handler.user.get_user_in_session(request)

        if request.method == 'GET':
            project_id = args[0]
        else :
            project_id = kw.get('pid')

        if not checker.check_permission(user=user, project_id=project_id, right_id=constants.right_upload_id):
            flash('You must have %s permission to share the project', 'error') % constants.right_upload
            raise redirect('/tracks', {'pid' : project_id})

        project = DBSession.query(Project).filter(Project.id == project_id).first()
        widget = form.ShareProject(action=url('/projects/share/%s' % project_id))

        # public url
        pub = url('/public/project', {'id' : project_id, 'k' : project.key})
       
        # download url
        if project.download_key is None:
            project.download_key = project.setdefaultkey()
        down = url('/public/project', {'id' : project_id, 'k' : project.download_key})


        widget.value = {'pid' : project_id}

        tl = handler.help.tooltip['links']
        tp = handler.help.tooltip['permissions']


        if request.method == 'POST':
            if kw.has_key('rights'):
                rights_checkboxes = kw.get('rights_checkboxes', None)
                if rights_checkboxes is not None:
                    if not isinstance(rights_checkboxes,list):
                        rights_checkboxes = [rights_checkboxes]
                    handler.project.change_rights(kw.get('pid'), kw.get('cid'), rights=rights_checkboxes)
                else : handler.project.change_rights(kw.get('pid'), kw.get('cid'))


            else :
                circle_ids = kw.get('circles', [])
                if not circle_ids: circle_ids = []
                if not isinstance(circle_ids, list):
                    circle_ids = [circle_ids]
                if len(circle_ids) > 0 and '' in circle_ids: circle_ids.remove('')
                handler.project.e(project=project, circle_ids=circle_ids)


        cr_data = [util.to_datagrid(datagrid.project_sharing, project.circles_rights, "Sharing", len(project.circles_rights)>0)]

        widget.child.children[1].options =  [('','')] + [(c.id, c.name) for c in user.circles_sharing if c not in project.shared_circles] +\
                                            [(c.id, c.name, {'selected' : True}) for c in project.shared_circles]

        return dict(page='projects', public=pub, download=down, name=project.name,
                    tooltip_permissions=tp, tooltip_links=tl, widget=widget, items=cr_data, project_id=project_id)


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

    def test(self, n):
        user = handler.user.get_user_in_session(request)
        p = handler.project.get_projects_with_permission(user.id, n)
        raise redirect('./')

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
        tracks = project.success_tracks

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
        info['plug_url'] = url('/plugins')

        info = json.dumps(info)

        control = 'b.showTracks();initGDV(b, %s, %s);' % (project.id, info)
        
        
        if 'loc' in kw:
            control += 'b.navigateTo("%s");' % kw['loc']
        
        # get jobs
        jobs = 'init_jobs = %s' % handler.job.jobs(project_id)
        
        # get operations
        try :
            ops = plugin.util.get_plugin_path()
            operations_path = 'init_operations = %s' % ops
            plug_url = plugin.util.form_url
        except Exception as e:
            print e
            ops = '[]'
            operations_path = 'init_operations = "connect"'
            plug_url = ''

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
        t = handler.help.tooltip['project']
        return dict(page='projects', model='project', tooltip=t, form_title="new project", projects=data_projects, value={})
