from tg import expose, flash, require, request, redirect, url, validate
import tg
from pygdv.lib import constants, checker, plugin
from pygdv.lib.base import BaseController
from pygdv.model import DBSession, Project, Track, Sequence
from repoze.what.predicates import has_any_permission
from pylons import tmpl_context
from formencode import Invalid
from pygdv import handler
import json, urllib, urllib2, os
from pygdv import handler
from pygdv.model import DBSession, Job
from bbcflib import gdv



class PluginController(BaseController):
    allow_only = has_any_permission(constants.perm_admin, constants.perm_user)

    @expose()
    def index(self, id, project_id, fl, *args, **kw):
        url = plugin.util.get_form_url()
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        req = {}
        # add private parameters
        user = handler.user.get_user_in_session(request)
        req['_up']= json.dumps({"key" : user.key, "mail" : user.email, "project_id" : project_id})
        fl = json.loads(fl)
        if len(fl) > 0 :
        # add tracks in the form
            gen_tracks = [[track.name, handler.track.plugin_link(track)] for track in project.success_tracks]
            for param in fl:
                req[param]= json.dumps(gen_tracks)
        req['id'] = id
        f = urllib2.urlopen(url, urllib.urlencode(req))
        return f.read()



    @expose()
    def callback(self, mail, key, project_id, fid, tid, st, tn, td, *args, **kw):
        print 'got callback %s (%s)' % (tid, st)
        user = handler.user.get_user_in_session(request)
        if st == 'RUNNING':
            # a new request is launched
            job = handler.job.new_job(name=tn, description=td, user_id=user.id, project_id=project_id, output='RUNNING', ext_task_id=tid)

            return {}

        elif st == 'SUCCESS' :
            print 'ok'
            # a request is finished
            # create new track
            if new_tracks.has_key(fid):
                result_output = os.path.join(constants.extra_directory(), tid)
                result_files = os.listdir(result_output)
                job = DBSession.query(Job).filter(Job.ext_task_id == tid).first()
                job.output = constants.JOB_TRACK
                index = 0
                for f in result_files:
                    _f = os.path.join(result_output, f)
                    res = gdv.single_track(mail=mail, key=key, serv_url=tg.config.get('main.proxy')+ tg.url('/'), project_id=project_id, fsys=_f)

                    if index == 0 :
                        # update current job
                        job.task_id = res.get('task_id')
                        job.data = res.get('track_id')
                        DBSession.add(job)

                    else :
                        # create new jobs
                        new_job = handler.job.new_job(name=job.name + ' (2)',
                            description=job.description + ' (2)',
                            user_id=user.id,
                            project_id=project_id,
                            output=job.output,
                            task_id=tid)
                        DBSession.add(new_job)

                DBSession.flush()
                return {}
            # job finished
            else :
                job = DBSession.query(Job).filter(Job.ext_task_id == tid).first()
                job.output = constants.SUCCESS
                # data will reference directoy where job outputs will be found
                job.data = os.path.join(constants.extra_url(), tid)
                DBSession.add(job)
                DBSession.flush()
                return {}

        elif st == 'ERROR' :

            job = DBSession.query(Job).filter(Job.ext_task_id == tid).first()
            job.output = constants.ERROR
            job.data = kw.get('error', 'an error occured')
            DBSession.add(job)
            DBSession.flush()
            return {}


