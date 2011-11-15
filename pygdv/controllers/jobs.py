# -*- coding: utf-8 -*-

from pygdv.lib.base import BaseController
from pygdv.lib import tequila, constants
from tg import expose,url,flash,request,response
from tg.controllers import redirect
from pygdv.model import User, Group, DBSession, Job
from paste.auth import auth_tkt
from pygdv.config.app_cfg import token
from paste.request import resolve_relative_url
import transaction
import datetime
from tg import app_globals as gl
import tg
from pygdv import handler

__all__ = ['JobController']



class JobController(BaseController):
    
    @expose()
    def result(self, id):
        return str(id)
    
    
    @expose()
    def traceback(self, id):
        job = DBSession.query(Job).filter(Job.id == id).first()
        return job.traceback