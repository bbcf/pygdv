from __future__ import absolute_import

from pygdv.lib.base import BaseController
from tg import expose, request
from repoze.what.predicates import has_any_permission
from tg import app_globals as gl
from pygdv.celery import tasks
from celery.task import chord
from pygdv import handler
from pygdv.model import DBSession, Project, Job
import track, json
from pygdv.lib import util, constants
import sys, traceback

__all__ = ['WorkerController']



class WorkerController(BaseController):
    allow_only = has_any_permission(gl.perm_admin, gl.perm_user)
    
    
    
    def index(self, *args, **kw):
        print 'worker received : args : %s, kw : %s' % (args, kw)
        pass
    
    @expose('json')
    def new_selection(self, project_id, s, job_name, job_description, *args, **kw):
        '''
        Called by the browser. Transform a selection to a new track;
        '''
        user = handler.user.get_user_in_session(request)
        sels = json.loads(s)
        print sels
        
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        if project is None :
            return {'error' : "project id %s doesn't exist" % project_id}
        path = track.common.temporary_path()
        
        with track.new(path, 'sql') as t:
            t.fields = ['start', 'end']
            for chromosome in sels:
                t.write(chromosome, [(marquee['start'], marquee['end']) for marquee in sels[chromosome]]);
            t.assembly = project.sequence.name
            
        rev = handler.track.create_track(user.id, project.sequence, f=path, trackname='%s %s' 
                                         % (job_name, job_description))
        if rev  == constants.NOT_SUPPORTED_DATATYPE :
            return {'error' : "not supported datatype" % project_id}
        return {'name' : job_name,
                'description' : job_description,
                'status' : 'running',
                'job_id' : rev}

    @expose('json')
    def status(self, job_id, *args, **kw):
        print 'status request %s : ' % (job_id)
        job = DBSession.query(Job).filter(Job.id == job_id).first()
        print job
        return {'job_id' : job.id, 'status' : job.status, 'output' : job.output, 'error' : job.traceback}
    
    
    
    
    
    @expose('json')
    def new_gfeatminer_job(self, project_id, job_description, job_name, data, *args, **kw):
        print 'new_gfeatminer_job pid : %s, data : %s, args : %s, kw : %s' % (project_id, data, args, kw)
        user = handler.user.get_user_in_session(request)
        try:
            data = json.loads(data)
        except Exception as e:
            return {'error': 'error when loading job in GDV', 'trace' : e.message}
        
        try:
            handler.job.parse_args(data)
        except IndexError as e:
            return {'error': 'you did not specified a requested parameter'}
        except Exception as e:
            return {'error': 'error when parsing job in GDV', 'trace' : e.message}
       
       
        
        try :
            job_id = handler.job.new_job(user.id, project_id, job_name, job_description, data, *args, **kw)
        except Exception as e:
            etype, value, tb = sys.exc_info()
            traceback.print_exception(etype, value, tb)
            return {'error': 'error when launching job in GDV', 'trace' : e.message}
        
        return {'job_id' : job_id,
                'job_name' : job_name,
                'job_description' : job_description,
                'status' : 'RUNNING'}
    
  
    