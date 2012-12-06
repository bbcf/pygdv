from tg import expose, request
import tg
from pygdv.lib import constants
from pygdv.lib.base import BaseController
from pygdv.model import DBSession, Project, Job, Bresults
from repoze.what.predicates import has_any_permission
from pygdv import handler
import json
import urllib
import urllib2
import os
from pygdv.model import Job, Result

file_tags = handler.job.file_tags()


class PluginController(BaseController):
    allow_only = has_any_permission(constants.permissions['admin']['name'], constants.permissions['read']['name'])

    @expose()
    def get(self, *args, **kw):
        print 'get %s, %s' % (args, kw)
        bsurl = handler.job.bioscript_url
        bsrequesturl = bsurl + '/plugins/get?id=' + kw['id']
        user = handler.user.get_user_in_session(request)
        project = DBSession.query(Project).filter(Project.id == kw['pid']).first()
        # add private parameters
        pp = {"key": user.key, "mail": user.email, "pid": project.id, "pkey": project.key}
        # add prefill parameters
        # TODO fetch tracks & selections
        req = urllib2.urlopen(url=bsrequesturl, data={'bs_private': {'app': pp, 'bs_cfg': handler.job.bioscript_config}})
        # display the form in template
        return req.read()

    @expose()
    def index(self, id, key, *args, **kw):
        bsurl = handler.job.bioscript_url
        shared_key = handler.job.shared_key
        project = DBSession.query(Project).filter(Project.key == key).first()
        req = {}
        # add private parameters
        user = handler.user.get_user_in_session(request)
        req['_up'] = json.dumps({"key": user.key, "mail": user.email, "project_key": project.key})
        req['key'] = shared_key
        # add prefill for parameters:
        gen_tracks = [[handler.track.plugin_link(track), track.name] for track in project.success_tracks]
        req['prefill'] = json.dumps({"track": gen_tracks})
        req['id'] = id
        bs_request_url = bsurl + '/plugins/get'
        f = urllib2.urlopen(bs_request_url, urllib.urlencode(req))
        return f.read()

    @expose()
    def validation(*args, **kw):
        print file_tags
        print 'validation %s, %s' % (args, kw)
        '''
        {'plugin_id': u'902ff1b6faeb24ea9e2574b3d4d6af3a82fa5130', 'task_id': u'62bc47e5-83c8-4abd-b631-317641f2237b'}
        '''

        return {}

    @expose()
    def callback(self, mail, key, project_id, fid, tid, st, tn, td, *args, **kw):
        print '##############################################'
        print 'got callback %s (%s)' % (tid, st)
        print '%s, %s, %s, %s, %s' % (fid, tn, td, args, kw)
        print '##############################################'
        user = handler.user.get_user_in_session(request)
        if st == 'RUNNING':
            # a new request is launched
            job = handler.job.new_job(name=tn, description=td, user_id=user.id, project_id=project_id, output='RUNNING', ext_task_id=tid)
            return {}

        elif st == 'SUCCESS':
            # a request is finished
            # look if there is file output
            job = DBSession.query(Job).filter(Job.ext_task_id == tid).first()

            if kw.has_key('fo'):
                fos = json.loads(kw.get('fo'))
                result_output = os.path.join(constants.extra_directory(), tid)
                result_files = os.listdir(result_output)
                for f in fos:
                    r = Result()
                    r.rtype = f[1]
                    r.rpath = os.path.join(result_output, f[0])
                    r.job_id = job.id

                    if r.rtype  in constants.track_types:
                        res = gdv.single_track(mail=mail, key=key, serv_url=tg.config.get('main.proxy')+ tg.url('/'),
                            project_id=project_id, fsys=r.rpath, delfile=True)
                        r.rmore = res
                        track_id = res.get('track_id')
                        r.track_id = track_id
                    DBSession.add(Result)

            # job finished
            job.output = constants.SUCCESS
            # data will reference directoy where job outputs will be found
            DBSession.add(job)
            DBSession.flush()
            return {}

        elif st == 'ERROR' :

            job = DBSession.query(Job).filter(Job.ext_task_id == tid).first()
            job.output = constants.ERROR
            job.data = kw.get('error', 'an unknown error occurred')
            DBSession.add(job)
            DBSession.flush()
            return {}


