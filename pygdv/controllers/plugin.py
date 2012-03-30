from tg import expose, flash, require, request, redirect, url, validate
from tg import app_globals as gl
from pygdv.lib import constants, checker
from pygdv.lib.base import BaseController
from pygdv.model import DBSession, Project, Track, Sequence
from repoze.what.predicates import has_any_permission
from pylons import tmpl_context
from formencode import Invalid
from pygdv import handler
from pygdv.model import DBSession, Project
from pygdv.celery import tasks
import json


class PluginController(BaseController):
    allow_only = has_any_permission(constants.perm_admin, constants.perm_user)
    
    @expose()
    def bad_form(self, *args, **kw):
        return 'bad form : %s' %  kw
    @expose()
    def test(self):
        tasks.test.delay((3,))
        return ''
    
    
    @expose('pygdv.templates.plugin_form')
    def get_form(self, form_id, project_id, *args, **kw):
        plug = handler.plugin.get_plugin_byId(form_id)
        if plug is None:
            kw['error'] = 'form not found'
            raise redirect(url('./bad_form', kw))
        
        user = handler.user.get_user_in_session(request)
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        if not checker.check_permission_project(user.id, project_id, constants.right_upload_id):
            kw['error'] = "you don't have permission to work on this project"
            raise redirect(url('./bad_form', kw))
        
        private_params={'user_id' : user.id,
                        'form_id' : form_id,
                        'project_id' : project_id}
        
        kw['_private_params'] = json.dumps(private_params)
        obj = plug.plugin_object
        tmpl_context.form = obj.output()(action='./validation')
        
        tmpl_context.tracks = project.tracks
        
        return {'page' : 'form', 'title' : obj.title(), 'value' : kw}

    @expose()
    def validation(self, *args, **kw):
        private_params = json.loads(kw.get('_private_params', False))
        if not private_params:
            raise redirect(url('./bad_form', kw))
        
        plug = handler.plugin.get_plugin_byId(private_params.get('form_id', False))
        
        form = plug.plugin_object.output()(action='validation')
        
        try:
            form.validate(kw, use_request_local=True)
        except Invalid as e:
            flash(e, 'error')
            kw['form_id']=private_params.get('form_id')
            kw['project_id']=private_params.get('project_id')
            raise redirect(url('./get_form', kw))
        
        kw['plugin_id'] = private_params.get('form_id')
        
        project = DBSession.query(Project).filter(Project.id == private_params['project_id']).first()
        job = handler.job.new_tmp_job(plug.plugin_object.title(), project.user_id, project.id)
        kw['job'] = job
        
        tasks.plugin_process.delay(**kw)
        
        flash('Job launched')
        
        kw['form_id']=private_params.get('form_id')
        kw['project_id']=private_params.get('project_id')
        raise redirect(url('./get_form',  kw))





