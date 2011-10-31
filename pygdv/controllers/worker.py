from __future__ import absolute_import

from pygdv.lib.base import BaseController
from tg import expose, request
from repoze.what.predicates import has_any_permission
from tg import app_globals as gl
from pygdv.celery import tasks
from celery.task import chord
from pygdv import handler
from pygdv.model import DBSession, Project
import track, json
from pygdv.lib import util, constants

__all__ = ['WorkerController']



class WorkerController(BaseController):
    allow_only = has_any_permission(gl.perm_admin, gl.perm_user)
    
    
    
    def index(self, *args, **kw):
        print 'worker received : args : %s, kw : %s' % (args, kw)
        pass
    
    @expose('json')
    def new_selection(self, project_id, s, job_name, job_description, *args, **kw):
        user = handler.user.get_user_in_session(request)
        sels = json.loads(s)
        print sels
        
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        if project is None :
            return {'error' : "project id %s doesn't exist" % project_id}
        path = track.common.temporary_path()
        _id = 1;
#        with track.new(path, 'sql') as t:
#            t.fields = ['start', 'end', 'name']
#            for selection in sels:
#                print 'selection : %s' % selection
#                print type(selection)
#                t.write(selection['chr'], ( (selection['start'], selection['end'], str(_id)), ))
#                _id += 1;
#            t.assembly = project.sequence.name
#            
#        ret = handler.track.create_track(user.id, project.sequence_id, f=path, trackname='%s %s' % (job_name, job_description))
        ret = 36
        if ret  == constants.NOT_SUPPORTED_DATATYPE :
            return {'error' : "not supported datatype" % project_id}
        return {'name' : job_name,
                'description' : job_description,
                'status' : 'running',
                'job_id' : ret}

    @expose('json')
    def status(self, *args, **kw):
        return {'job_id' : 36, 'status' : constants.SUCCESS, 'output' : 'reload',
                }
    