# -*- coding: utf-8 -*-

from pygdv.lib.base import BaseController
from pygdv.lib import tequila, constants
from tg import expose, url, flash, request, response, tmpl_context
from tg.controllers import redirect
from pygdv.model import User, Group, DBSession, Job
from paste.auth import auth_tkt
from pygdv.config.app_cfg import token
from paste.request import resolve_relative_url
import transaction
import datetime
from tg import app_globals as gl
import tg, os
from pygdv import handler
from pygdv.lib import util
from pygdv.widgets.job import job_grid

__all__ = ['JobController']



class JobController(BaseController):
    
    @expose('pygdv.templates.image')
    def result(self, id):
        job = DBSession.query(Job).filter(Job.id == id).first()
        if job is not None:
            data = util.to_datagrid(job_grid, [job])
        
        path = path = os.path.join('/data', 'gfeatminer', str(job.id))
        filename = os.listdir(path)
        
        final = os.path.join(path, filename)
        
        tmpl_context.src = url(final)

        return dict(page='jobs', model='Job', info=data)
        
        
        return str(id)
    
    
    @expose()
    def traceback(self, id):
        job = DBSession.query(Job).filter(Job.id == id).first()
        return job.traceback