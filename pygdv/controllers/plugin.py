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

fill_with_tracks = {'dd2f5c97a48ab83caa5618a3a8898c54205c91b5' : ['track_1', 'track_2']}
new_tracks = {'dd2f5c97a48ab83caa5618a3a8898c54205c91b5' : True}


class PluginController(BaseController):
    allow_only = has_any_permission(constants.perm_admin, constants.perm_user)

    @expose()
    def index(self, id, project_id, *args, **kw):
        url = plugin.util.get_form_url()
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        req = {}
        # add private parameters
        user = handler.user.get_user_in_session(request)
        req['_up']= json.dumps({"key" : user.key, "mail" : user.email, "project_id" : project_id})

        # add tracks in the form
        if fill_with_tracks.has_key(id):
            gen_tracks = [[track.name, handler.track.plugin_link(track)] for track in project.success_tracks]
            for param in fill_with_tracks.get(id):
                req[param]= json.dumps(gen_tracks)
        req['id'] = id
        f = urllib2.urlopen(url, urllib.urlencode(req))
        return f.read()



    @expose()
    def callback(self, mail, key, project_id, form_id, task_id, status, *args, **kw):
        user = handler.user.get_user_in_session(request)
        print 'callback'
        print args
        print kw
        print status

        if status == 'RUNNING':
            # a new request is launched
            job = handler.job.new_job(name='NEW JOB', description='a new job', user_id=user.id, project_id=project_id, output='no output for the moment', ext_task_id=task_id)
            print 'new job %s' % job
            return {}

        elif status == 'SUCCESS' :
            # a request is finished
            # TODO update job
            # create new track
            if new_tracks.has_key(form_id):
                """
                {'status': u'SUCCESS',
                'form_id': u'dd2f5c97a48ab83caa5618a3a8898c54205c91b5',
                'task_id': u'7a9c406a-3e56-4728-8589-03d31aab37e5',
                'result': u'files merged',
                'key': u'b8a05c98-5082-4cf2-976e-59b916e9e62a',
                'mail': u'yohan.jarosz@epfl.ch'}
                """
                result_output = os.path.join(constants.extra_directory(), task_id)
                result_files = os.listdir(result_output)
                job = DBSession.query(Job).filter(Job.ext_task_id == task_id).first()
                job.output = constants.JOB_TRACK
                index = 0
                for f in result_files:
                    _f = os.path.join(result_output, f)
                    print _f
                    res = gdv.single_track(mail=mail, key=key, serv_url=tg.config.get('main.proxy'), project_id=project_id, fsys=_f)
                    if index == 0 :
                        # update current job
                        job.task_id = res.get('task_id')
                        DBSession.add(job)
                    else :
                        # create new jobs
                        new_job = handler.job.new_job(name=job.name + ' (2)',
                            description=job.description + ' (2)',
                            user_id=user.id,
                            project_id=project_id,
                            output=job.output,
                            task_id=task_id)
                        DBSession.add(new_job)
                    print res

                DBSession.flush()

                return {}
            else :
                job = DBSession.query(Job).filter(Job.ext_task_id == task_id).first()
                job.output = constants.SUCCESS
                DBSession.add(job)
                DBSession.flush()
                return {}

        elif status == 'ERROR' :
            job = DBSession.query(Job).filter(Job.ext_task_id == task_id).first()
            job.output = constants.ERROR
            DBSession.add(job)
            DBSession.flush()
            return {}


