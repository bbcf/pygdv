from tg import expose, request
import tg
from pygdv.lib import constants, filemanager
from pygdv.lib.base import BaseController
from pygdv.model import DBSession, Project, Job, Bresults, User, Track
from repoze.what.predicates import has_any_permission
from pygdv import handler
import json
import urllib
import urllib2
import os
from pygdv.worker import tasks

file_tags = handler.job.file_tags()

args_list = ['key', 'mail', 'pid', 'pkey', 'plugin_id', 'task_id']


class PluginController(BaseController):
    allow_only = has_any_permission(constants.permissions['admin']['name'], constants.permissions['read']['name'])

    @expose()
    def get(self, *args, **kw):
        bsurl = handler.job.bioscript_url
        bsrequesturl = bsurl + '/plugins/get?id=' + kw['id']
        user = handler.user.get_user_in_session(request)
        project = DBSession.query(Project).filter(Project.id == kw['pid']).first()
        # add private parameters
        pp = {"key": user.key, "mail": user.email, "pid": project.id, "pkey": project.key}
        # add prefill parameters
        tracks = list(project.tracks)
        selections = list(project.selections)
        gtrack = [(handler.track.plugin_link(t), t.name) for t in tracks]
        if len(selections) > 0:
            s = selections[0]
            if len(s.locations) > 0:
                gtrack.append((handler.track.plugin_link(s, selection_id=s.id), 'selection'))

        prefill = json.dumps({'track': gtrack})

        # TODO fetch tracks & selections
        req = urllib2.urlopen(url=bsrequesturl, data=urllib.urlencode({
            'key': handler.job.shared_key,
            'bs_private': json.dumps({'app': pp, 'cfg': handler.job.bioscript_config,
            'prefill': prefill})}))
        # display the form in template
        return req.read()

    # @expose()
    # def index(self, id, key, *args, **kw):
    #     bsurl = handler.job.bioscript_url
    #     shared_key = handler.job.shared_key
    #     project = DBSession.query(Project).filter(Project.key == key).first()
    #     req = {}
    #     # add private parameters
    #     user = handler.user.get_user_in_session(request)
    #     req['_up'] = json.dumps({"key": user.key, "mail": user.email, "project_key": project.key})
    #     req['key'] = shared_key
    #     # add prefill for parameters:
    #     gen_tracks = [[handler.track.plugin_link(track), track.name] for track in project.success_tracks]
    #     req['prefill'] = json.dumps({"track": gen_tracks})
    #     req['id'] = id
    #     bs_request_url = bsurl + '/plugins/get'
    #     f = urllib2.urlopen(bs_request_url, urllib.urlencode(req))
    #     return f.read()

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
        job.status = 'PENDING'
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
        print kw
        job = DBSession.query(Job).filter(Job.ext_task_id == kw['task_id']).first()
        project = DBSession.query(Project).filter(Project.id == int(kw['pid'])).first()
        if project is None or project.key != str(kw['pkey']):
            raise Exception('Project not valid')
        if job.project_id != project.id:
            raise Exception('Job not valid')

        status = str(kw['status'])
        job.status = status
        if status.lower() in ['error', 'failed']:
            job.traceback = kw['error']
        elif status == 'SUCCESS':
            results = json.loads(kw['results'])
            for result in results:
                bres = Bresults()
                bres.job_id = job.id
                bres.output_type = str(result.get('type', 'not defined'))
                bres.is_file = result.get('is_file', False)
                path = str(result.get('path', ''))
                bres.path = path
                bres.data = str(result.get('value', ''))

                is_track = result.get('type', '') == 'track'
                if is_track:
                    out = os.path.join(filemanager.temporary_directory(), os.path.split(path)[-1])
                    fileinfo = filemanager.FileInfo(inputtype='fsys', inpath=path, outpath=out, admin=False)
                    sequence = project.sequence
                    user = DBSession.query(User).filter(User.key == str(kw['key'])).first()
                    if user.email != str(kw['mail']):
                        raise Exception("Wrong user")
                    user_info = {'id': user.id, 'name': user.name, 'email': user.email}
                    sequence_info = {'id': sequence.id, 'name': sequence.name}

                    t = Track()
                    t.name = fileinfo.trackname
                    t.sequence_id = sequence.id
                    t.user_id = user.id
                    DBSession.add(t)
                    DBSession.flush()
                    async = tasks.new_input.delay(user_info, fileinfo, sequence_info, t.id, project.id)
                    t.task_id = async.task_id
                    bres.track_id = t.id

                bres.is_track = is_track
                DBSession.add(bres)
        DBSession.flush()
        return {}
