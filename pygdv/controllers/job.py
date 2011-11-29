# -*- coding: utf-8 -*-

from tgext.crud import CrudRestController
from pygdv.lib import tequila, constants
from tg import expose, url, flash, request, response, tmpl_context
from tg.controllers import redirect
from pygdv.model import User, Group, DBSession, Job
from pygdv.config.app_cfg import token
import transaction
import datetime
from tg import app_globals as gl
import tg, os
from repoze.what.predicates import has_any_permission
from pygdv import handler
from pygdv.lib import util, constants
from pygdv.widgets.job import job_grid
from pygdv.widgets.job import job_edit_filler, job_edit_form, job_grid, job_new_form, job_table, job_table_filler
from tg.decorators import paginate, with_trailing_slash,without_trailing_slash
from sqlalchemy.sql import and_, or_, not_

__all__ = ['JobController']



class JobController(CrudRestController):
    allow_only = has_any_permission(constants.perm_user, constants.perm_admin)
    model = Job
    table = job_table
    table_filler = job_table_filler
    edit_form = job_edit_form
    new_form = job_new_form
    edit_filler = job_edit_filler
    
    
    @with_trailing_slash
    @expose('pygdv.templates.list')
    def get_all(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        jobs = DBSession.query(Job).filter(and_(Job.user_id == user.id, not_(Job.output == constants.job_output_reload))).all()
        data = [util.to_datagrid(job_grid, jobs, "Job Listing", len(jobs)>0)]
        return dict(page='jobs', model='job', form_title="new job", items=data, value=kw)
    
    
    @expose('pygdv.templates.image')
    def result(self, id):
        job = DBSession.query(Job).filter(Job.id == id).first()
        if job is not None:
            data = util.to_datagrid(job_grid, [job])
        
        path = path = os.path.join(constants.gfeatminer_directory(), str(job.id))
        
        filename = os.listdir(path)[0]
        print filename
        
        final = os.path.join(constants.gfeatminer_url(),  str(job.id), filename)
        
        tmpl_context.src = url(final)

        return dict(page='jobs', model='Job', info=data)
        
        
        return str(id)
    
    
    @expose()
    def traceback(self, id):
        job = DBSession.query(Job).filter(Job.id == id).first()
        return job.traceback
    
    
    
    
    
    