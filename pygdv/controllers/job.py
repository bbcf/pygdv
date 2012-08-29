# -*- coding: utf-8 -*-

from tgext.crud import CrudRestController
from pygdv.lib import tequila, constants
from pygdv.lib.base import BaseController
from tg import expose, url, flash, request, response, tmpl_context
from tg.controllers import redirect
from pygdv.model import User, Group, DBSession, Job, Result
from pygdv.config.app_cfg import token
import transaction
import datetime
from tg import app_globals as gl
import tg, os
from repoze.what.predicates import has_any_permission
from pygdv import handler
from pygdv.lib import util, constants, checker
from pygdv.widgets.job import job_grid
from pygdv.widgets.job import job_edit_filler, job_edit_form, job_grid, job_new_form, job_table, job_table_filler
from tg.decorators import paginate, with_trailing_slash,without_trailing_slash
from sqlalchemy.sql import and_, or_, not_
from pygdv.widgets import datagrid

__all__ = ['JobController']



class JobController(BaseController):
    allow_only = has_any_permission(constants.perm_user, constants.perm_admin)

    @with_trailing_slash
    @expose('pygdv.templates.jobs_index')
    def index(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if request.method == 'POST':
            jid = kw.get('id', None)
            if jid is not None and checker.can_edit_job(user.id, jid):
                handler.job.delete(jid)
            else:
                flash('not authorized')

        jobs = DBSession.query(Job).filter(Job.user_id == user.id).all()

        data = [{'title' : job.name,
                 'isFolder' : True,
                 'children' : [{'title' : res.rtype} for res in job.results ]} for job in jobs]
        data = util.to_datagrid(datagrid.job_grid, jobs, "Job Listing", grid_display=len(jobs)>0)
        t = handler.help.help_address(url('/help'), 'jobs', 'How to compute new data')

        return dict(page='jobs', model='job', form_title="new job", item=data, value=kw, tooltip=t)
    
    @without_trailing_slash
    @expose()
    def new(self, *args, **kw):
        return "You can launch jobs from project view"
    
    
    
    @expose('pygdv.templates.job')
    def result(self, id):

        res = DBSession.query(Result).filter(Result.id == id).first()
        checker.check_permission(user=handler.user.get_user_in_session(request),
            project=res.job.project, right_id=constants.right_download_id)
        if res.rtype in constants.track_types:
            raise redirect(url('/tracks/links/%s' % res.track_id))

        src = constants.extra_url() + '/' + res.rpath
        return dict(page='jobs', model='Job', src=src)

    
    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        _id = args[0]
        if not checker.can_edit_job(user.id, _id):
            flash("You haven't the right to edit a job which is not yours")
            raise redirect('../')
        handler.job.delete(_id)
        raise redirect('./')

    @expose('json')
    def _delete(self, _id):
        user = handler.user.get_user_in_session(request)
        if not checker.can_edit_job(user.id, _id):
            return {'error' : "You have don't have the right to delete this job"}
        handler.job.delete(_id)
        return {'success' : 'job deleted'}
    
    @expose('json')
    def get_jobs(self, project_id, *args, **ke):
        user = handler.user.get_user_in_session(request)
        if not checker.check_permission_project(user.id, project_id, constants.right_read_id):
            return {'error' : "You haven't the right to read this project"}
        
        jobs = DBSession.query(Job).filter(and_(Job.user_id == user.id, Job.project_id == project_id, not_(and_(Job.output == constants.job_output_reload, Job.status == 'SUCCESS')))).all()
        return {'jobs' : jobs}
    
        
    @expose()
    def traceback(self, id):
        job = DBSession.query(Job).filter(Job.id == id).first()
        return job.traceback
    
    
    
    
    
    