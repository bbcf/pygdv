"""Project Controller"""

from repoze.what.predicates import has_any_permission, has_permission
from pygdv.lib.base import BaseController
from tg import expose, flash, require, request, url
from tg.controllers import redirect
from tg.decorators import with_trailing_slash
from pygdv.widgets import datagrid

from pygdv.model import DBSession, Project, User, Species, Track, Sequence
from pygdv.widgets import form
from pygdv import handler
from pygdv.lib import util
from pygdv.lib import checker
from pygdv.lib import constants, reply
import tw2.core as twc
from sqlalchemy.sql import and_, not_
import json

__all__ = ['ProjectController']

DEBUG_LEVEL = 0


def debug(s, t=0):
    if DEBUG_LEVEL > 0:
        print '[project controller] %s%s' % ('\t' * t, s)


class ProjectController(BaseController):
    allow_only = has_any_permission(constants.permissions['admin']['name'], constants.permissions['read']['name'])

    @expose('pygdv.templates.project_new')
    def new(self, *args, **kw):
        new_form = form.NewProject(action=url('/projects/create')).req()
        species = DBSession.query(Species).all()
        sp_opts = [(sp.id, sp.name) for sp in species]
        new_form.child.children[2].options = sp_opts
        mapping = json.dumps(dict([(sp.id, [(seq.id, seq.name) for seq in sp.sequences
                                    if seq.public or handler.genrep.checkright(seq, user)]) for sp in species]))
        new_form.value = {'smapping': mapping}
        return dict(page='projects', widget=new_form)

    @with_trailing_slash
    @expose('pygdv.templates.project_edit')
    def edit(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if request.method == 'GET':
            project_id = args[0]
        else:
            project_id = kw.get('pid')
        debug("check permission", 1)
        if not checker.check_permission(user=user, project_id=project_id, right_id=constants.right_upload_id) and not checker.is_admin(user=user):
            flash('You must have %s permission to edit the project.' % constants.right_upload, 'error')
            raise redirect('/tracks/', {'pid': project_id})
        #if checker.is_admin(user=user):
            #user = DBSession.query(User).join(Project).filter(Project.id == project_id).first()

        widget = form.EditProject(action=url('/projects/edit/%s' % project_id)).req()
        widget.value = {'pid': project_id}
        project = DBSession.query(Project).filter(Project.id == project_id).first()

        # prendre les user tracks du meme sequence id
        tracks = DBSession.query(Track).join(User.tracks).filter(
            and_(User.id == user.id, Track.sequence_id == project.sequence_id,
                not_(Track.id.in_([t.id for t in project.tracks])))
        ).all()

        if request.method == 'GET':
            debug("GET", 2)
            widget.child.children[1].value = project.name
            widget.child.children[2].options = [('', '')] + [(t.id, t.name) for t in tracks] + [(t.id, t.name, {'selected': True}) for t in project.tracks]
            return dict(page='tracks', widget=widget, project_id=project_id)
        debug("POST", 2)
        try:
            debug("validate post", 2)
            widget.validate(kw)
        except twc.ValidationError as e:
            debug("error", 2)
            w = e.widget
            w.child.children[1].value = project.name
            w.child.children[2].options = [(t.id, t.name) for t in tracks] + [(t.id, t.name, {'selected': True}) for t in project.tracks]
            return dict(page='tracks', widget=w, project_id=project_id)
        debug("validation passed")
        track_ids = kw.get('tracks', [])
        if not track_ids:
            track_ids = []
        if not isinstance(track_ids, list):
            track_ids = [track_ids]
        if len(track_ids) > 0 and '' in track_ids:
            track_ids.remove('')

        # if the project is shared, add all project track_ids
        if not checker.own(user=user, project=project):
            for t in project.tracks:
                if not checker.user_own_track(user.id, track=t) and t.id not in track_ids:
                    track_ids.append(t.id)

        handler.project.e(project_id=project_id, name=kw.get('name'), track_ids=track_ids)
        raise redirect('/tracks/', {'pid': project_id})

    @expose('json')
    def get(self, project_key=None, project_id=None, **kw):
        if not project_key and not project_id:
            user = handler.user.get_user_in_session(request)
            projects = DBSession.query(Project).filter(Project.user_id == user.id).all()
            return reply.normal(request, 'You can upload track on these projects', '/tracks', {'projects': projects})
        project = None
        if project_id is not None and project_id:
            user = handler.user.get_user_in_session(request)
            project = DBSession.query(Project).filter(Project.id == int(project_id)).first()
            if project is not None and not project.user_id == user.id:
                reply.error(request, 'Not your project', '/tracks', {})
        else:
            project = DBSession.query(Project).filter(Project.key == project_key).first()
        if project is None:
            return reply.error(request, 'Wrong key', '/tracks', {})
        user = handler.user.get_user_in_session(request)
        if not checker.check_permission_project(user.id, project.id, constants.right_upload_id):
            return reply.error(request, 'Wrong key', '/tracks', {})
        else:
            return reply.normal(request, 'You can upload track on this project', '/tracks', {'project': project})

    @expose('json')
    def create(self, *args, **kw):
        print 'create %s, %s' % (args, kw)
        user = handler.user.get_user_in_session(request)
        if not 'name' in kw:
            return reply.error(request, 'Missing project `name`.', url('/tracks'), {})

        if not 'assembly' in kw:
            return reply.error(request, 'Missing project `assembly` identifier.',  url('/tracks'), {})

        sequence = DBSession.query(Sequence).filter(Sequence.id == int(kw.get('assembly'))).first()
        if sequence is None:
            return reply.error(request, "Assembly doesn't exist in GDV.", './', {})

        project = handler.project.create(kw['name'], kw['assembly'], user.id)
        return reply.normal(request, 'Project successfully created.',  url('/tracks'), {'project': project})

    @expose()
    def post(self, *args, **kw):
        return self.create(*args, **kw)

    @expose('json')
    def delete(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if len(args) > 0:
            project_id = args[0]
            if not checker.check_permission(user=user, project_id=project_id, right_id=constants.right_upload_id) and not checker.is_admin(user=user):
                return reply.error(request, "You must have %s permission to delete the project." % constants.right_upload,
                        '/tracks', {'error': 'wrong credentials'})

        handler.project.delete(project_id=project_id)
        return reply.normal(request, 'Project successfully deleted.', '/tracks', {'success': 'project deleted'})

    @expose('pygdv.templates.project_sharing')
    def share(self, *args, **kw):
        user = handler.user.get_user_in_session(request)

        if request.method == 'GET':
            project_id = args[0]
        else:
            project_id = kw.get('pid')

        if not checker.check_permission(user=user, project_id=project_id, right_id=constants.right_upload_id) and not checker.is_admin(user=user):
            flash('You must have %s permission to share the project', 'error') % constants.right_upload
            raise redirect('/tracks', {'pid': project_id})

        project = DBSession.query(Project).filter(Project.id == project_id).first()
        widget = form.ShareProject(action=url('/projects/share/%s' % project_id))

        # public url
        pub = url('/public/project', {'id': project_id, 'k': project.key})
        # download url
        if project.download_key is None:
            project.download_key = project.setdefaultkey()
        down = url('/public/project', {'id': project_id, 'k': project.download_key})

        widget.value = {'pid': project_id}

        tl = handler.help.help_address(url('help'), '#share', 'sharing projects')

        if request.method == 'POST':
            if kw.has_key('rights'):
                rights_checkboxes = kw.get('rights_checkboxes', None)
                if rights_checkboxes is not None:
                    if not isinstance(rights_checkboxes,list):
                        rights_checkboxes = [rights_checkboxes]
                    handler.project.change_rights(kw.get('pid'), kw.get('cid'), rights=rights_checkboxes)
                else: handler.project.change_rights(kw.get('pid'), kw.get('cid'))


            else:
                circle_ids = kw.get('circles', [])
                if not circle_ids: circle_ids = []
                if not isinstance(circle_ids, list):
                    circle_ids = [circle_ids]
                if len(circle_ids) > 0 and '' in circle_ids: circle_ids.remove('')
                handler.project.e(project=project, circle_ids=circle_ids)

        debug(project.get_circle_with_right_display)

        cr_data = [util.to_datagrid(datagrid.project_sharing, project.circles_rights, "Sharing", len(project.circles_rights)>0)]

        widget.child.children[1].options =  [('','')] + [(c.id, c.name) for c in user.circles_sharing if c not in project.shared_circles] +\
                                            [(c.id, c.name, {'selected': True}) for c in project.shared_circles]

        return dict(page='projects', public=pub, download=down, name=project.name,
            tooltip_links=tl, widget=widget, items=cr_data, project_id=project_id)

    @expose('pygdv.templates.view')
    def view(self, project_id, *args, **kw):
        debug('VIEW')
        user = handler.user.get_user_in_session(request)
        if not checker.check_permission(project_id=project_id, user=user, right_id=constants.rights['read']['id']):
            flash('You must have %s permission to view the project.' % constants.right_read, 'error')
            raise redirect(url('/'))
        d = handler.view.prepare_view(project_id, *args, **kw)
        return d

    @require(has_permission('admin', msg='Only for admins'))
    @expose('pygdv.templates.admin_project')
    def admin(self):
        projects = DBSession.query(Project).all()
        data_projects = [util.to_datagrid(project_admin_grid, projects, "All projects", len(projects) > 0)]
        t = handler.help.tooltip['project']
        return dict(page='projects', model='project', tooltip=t, form_title="new project", projects=data_projects, value={})
