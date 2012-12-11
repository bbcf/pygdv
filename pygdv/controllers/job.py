# -*- coding: utf-8 -*-

from pygdv.lib import constants
from pygdv.lib.base import BaseController
from tg import expose, url, flash, request
from tg.controllers import redirect
from pygdv.model import DBSession, Job, Bresults
from repoze.what.predicates import has_any_permission
from pygdv import handler
from pygdv.lib import util, checker
from tg.decorators import with_trailing_slash, without_trailing_slash
from sqlalchemy.sql import and_, not_
from pygdv.widgets import datagrid

__all__ = ['JobController']


class JobController(BaseController):
    allow_only = has_any_permission(constants.permissions['admin']['name'], constants.permissions['read']['name'])

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

        data = util.to_datagrid(datagrid.job_grid, jobs, "Job Listing", grid_display=len(jobs) > 0)
        t = handler.help.help_address(url('/help'), 'jobs', 'How to compute new data')

        return dict(page='jobs', model='job', form_title="new job", item=data, value=kw, tooltip=t)

    @expose('pygdv.templates.job')
    def result(self, id):

        res = DBSession.query(Bresults).filter(Bresults.id == id).first()
        checker.check_permission(user=handler.user.get_user_in_session(request),
            project=res.job.project, right_id=constants.right_download_id)
        if res.rtype in constants.track_types:
            raise redirect(url('/tracks/links/%s' % res.track_id))

        src = constants.extra_url() + '/' + res.rpath
        return dict(page='jobs', model='Job', src=src)

    @expose('json')
    def delete(self, _id):
        user = handler.user.get_user_in_session(request)
        if not checker.can_edit_job(user.id, _id):
            return {'error': "You have don't have the right to delete this job"}
        job = DBSession.query(Job).filter(Job.id == _id).first()
        # TODO delete results (DB + filesystem)
        DBSession.delete(job)
        raise redirect('/jobs')

    @expose()
    def traceback(self, id):
        job = DBSession.query(Job).filter(Job.id == id).first()
        if job.traceback:
            return job.traceback
        return 'no traceback.'
