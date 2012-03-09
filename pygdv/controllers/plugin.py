from tg import expose, flash, require, request, redirect, url, validate
from tg import app_globals as gl
from pygdv.lib import constants
from pygdv.lib.base import BaseController
from pygdv.model import DBSession, Project, Track, Sequence
from repoze.what.predicates import has_any_permission
from yapsy.PluginManager import PluginManager
from pylons import tmpl_context
from pygdv.widgets.plugins.form import exampleform
from formencode import Invalid



class PluginController(BaseController):
    
    
    def index(self, *args, **kw):
        return 'got *args (%s), **kw(%s)' % (args, kw)
    
    
    @expose('pygdv.templates.plugin_form')
    def get_form(self, name, *args, **kw):
        plug = gl.plugin_manager.getPluginByName(name)
        if plug is None:
            raise redirect(url('./'))

        tmpl_context.form = plug.plugin_object.output()(action='validation')
        kw['_plugin_name'] = name
        return {'page' : 'form', 'value' : kw}

    @expose()
    def validation(self, _plugin_name, *args, **kw):
        plug = gl.plugin_manager.getPluginByName(_plugin_name)
        kw['_plugin_name'] = _plugin_name
        if plug is None:
            flash('Validation failed', 'error')
            raise redirect(url('./get_form'))

        form = plug.plugin_object.output()(action='validation')
        try:
            form.validate(kw, use_request_local=True)
        except Invalid as e:
            flash(e, 'error')
            raise redirect(url('./get_form', {'name':_plugin_name}))
        
        raise redirect(url('./ok', **kw))


    @expose()
    def ok(self, *args, **kw):
        return 'got %s, %s'% (args, kw)



