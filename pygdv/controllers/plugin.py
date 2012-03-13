from tg import expose, flash, require, request, redirect, url, validate
from tg import app_globals as gl
from pygdv.lib import constants
from pygdv.lib.base import BaseController
from pygdv.model import DBSession, Project, Track, Sequence
from repoze.what.predicates import has_any_permission
from yapsy.PluginManager import PluginManager
from pylons import tmpl_context
from formencode import Invalid
from pygdv import handler
from pygdv.widgets.plugins.form import ExampleForm



class PluginController(BaseController):
    
    
    def index(self, *args, **kw):
        return 'got *args (%s), **kw(%s)' % (args, kw)
    
    @expose()
    def bad_form(self, *args, **kw):
        return 'bad form : got *args (%s), **kw(%s)' % (args, kw)
    
    
    @expose('pygdv.templates.plugin_form')
    def get_form(self, *args, **kw):
        plug = handler.plugin.get_plugin_byId(kw.get('form_id', False))
        if plug is None:
            raise redirect(url('./bad_form'))
        obj = plug.plugin_object
        tmpl_context.form = obj.output()(action='./validation')
        kw['form_id'] = kw.get('form_id')
        return {'page' : 'form', 'title' : obj.title(), 'value' : kw}

    @expose()
    def validation(self, form_id, *args, **kw):
        plug = handler.plugin.get_plugin_byId(form_id)
        print plug
        kw['form_id'] = form_id
        if plug is None:
            flash('Validation failed', 'error')
            raise redirect(url('./get_form'))
        
        
        
        form = plug.plugin_object.output()(action='validation')
        
        try:
            form.validate(kw, use_request_local=True)
        except Invalid as e:
            flash(e, 'error')
            raise redirect(url('./get_form', {'form_id':form_id}))
        
        raise redirect(url('./ok', **kw))


    @expose()
    def ok(self, *args, **kw):
        return 'got %s, %s'% (args, kw)



