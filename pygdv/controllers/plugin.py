from tg import expose, flash, require, request, redirect, url, validate
from tg import app_globals as gl
from pygdv.lib import constants, checker, plugin
from pygdv.lib.base import BaseController
from pygdv.model import DBSession, Project, Track, Sequence
from repoze.what.predicates import has_any_permission
from pylons import tmpl_context
from formencode import Invalid
from pygdv import handler
from pygdv.model import DBSession, Project
from pygdv.celery import tasks
import json, urllib, urllib2


fill = {'dd2f5c97a48ab83caa5618a3a8898c54205c91b5' : ['track_1', 'track_2']}



class PluginController(BaseController):
    allow_only = has_any_permission(constants.perm_admin, constants.perm_user)

    @expose()
    def index(self, id, project_id, *args, **kw):
        url = plugin.util.get_form_url()
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        req = {}
        if fill.has_key(id):
            gen_tracks = [[track.name, handler.track.plugin_link(track)] for track in project.tracks]

            for param in fill.get(id):
                req[param]= json.dumps(gen_tracks)
        req['id'] = id
        f = urllib2.urlopen(url, urllib.urlencode(req))
        return f.read()



    @expose()
    def callback(self, *args, **kw):
        print 'callback'
        print args
        print kw
        return {}
