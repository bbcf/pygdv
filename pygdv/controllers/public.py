from pygdv.lib.base import BaseController
from pygdv.lib import tequila, constants
from tg import expose,url,flash,request,response
from tg.controllers import redirect
from pygdv.model import User, Group, DBSession
from pygdv.config.app_cfg import token
import transaction
import datetime
from tg import app_globals as gl
import tg
from pygdv.model import DBSession, Project, Job
from pygdv.lib.jbrowse import util as jb
from pygdv.lib import constants, reply
from pygdv.celery import tasks
import json
from sqlalchemy import and_, not_

from pygdv import handler

__all__ = ['LoginController']



class PublicController(BaseController):
    

    @expose('pygdv.templates.view')
    def project(self, id, k, **kw):
        project = DBSession.query(Project).filter(Project.id == id).first()
        if project is None:
            flash('wrong link', 'error')
            raise redirect(url('/home'))
        mode = None

#        if not GenRep().is_up():
#            raise redirect(url('/error', {'m': 'Genrep service is down. Please try again later.'}))


        if k == project.key : mode = 'read'
        elif k == project.download_key : mode = 'download'

        if mode is None :
            flash('wrong link', 'error')
            raise redirect(url('/home'))

        kw['mode'] = mode
        kw['admin'] = False
        d = handler.view.prepare_view(project.id, **kw)
        return d
        
        
        
        
      
            