from tg import expose, request
import tg
from pygdv.lib import constants
from pygdv.lib.base import BaseController
from pygdv.model import DBSession, Project, Job, Bresults, User
from repoze.what.predicates import has_any_permission
from pygdv import handler
import json
import urllib
import urllib2
import os

file_tags = handler.job.file_tags()

args_list = ['key', 'mail', 'pid', 'pkey', 'plugin_id', 'task_id']


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
        prefill = []
        # TODO fetch tracks & selections
        # add shared key
        req = urllib2.urlopen(url=bsrequesturl, data=urllib.urlencode({
            'key': handler.job.shared_key,
            'bs_private': json.dumps({'app': pp, 'cfg': handler.job.bioscript_config,
            'prefill': prefill})}))
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
        for arg in args_list:
            if arg not in kw:
                raise Exception('Missing args for the validation %s' % kw)
        user = DBSession.query(User).filter(User.email == str(kw['mail'])).first()
        if user.key != str(kw['key']):
            raise Exception('User not valid %s' % kw)
        project = DBSession.query(Project).filter(Project.id == int(kw['pid'])).first()
        if project.key != str(kw['pkey']):
            raise Exception('Project not valid %s' % kw)
        job = Job()
        job.user_id = user.id
        job.project_id = project.id
        job.status = 'RUNNING'
        job.ext_task_id = kw['task_id']
        job.bioscript_url = handler.job.task_url(kw['task_id'])
        if 'plugin_info' in kw:
            info = json.loads(kw['plugin_info'])
            job.name = info['title']
            job.description = info['description']
        else:
            job.name = 'Job %s from bioscript' % kw['task_id']
            job.description = 'Description available at %s' % handler.job.task_url(kw['task_id'])
        DBSession.add(job)
        DBSession.flush()
        return {}

    @expose()
    def callback(self, *args, **kw):
        print '##############################################'
        print 'got callback %s (%s)' % (args, kw)
        return {}


