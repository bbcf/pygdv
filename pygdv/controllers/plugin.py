from tg import expose, flash, require, request, redirect, url, validate
from tg import app_globals as gl
from pygdv.lib import constants
from pygdv.lib.base import BaseController
from pygdv.model import DBSession, Project, Track, Sequence
from repoze.what.predicates import has_any_permission
from yapsy.PluginManager import PluginManager
from pylons import tmpl_context
from pygdv.widgets.plugins.form import exampleform


def get_form(*args, **kw):
    print 'sdsdsd'
    from tw.forms import validators as twv
    return exampleform

class PluginController(BaseController):
    
    
    @expose()
    def index(self, *args, **kw):
        return 'got *args (%s), **kw(%s)' % (args, kw)
    
    
    @expose('pygdv.templates.plugin_form')
    def test(self, *args, **kw):
        plug = gl.plugin_manager.getPluginByName('TestPlugin')
        if not plug:
            raise redirect(url('./'))
        
        tmpl_context.form = exampleform
        
        kw['_plugin_name'] = 'TestPlugin'
        
        return {'page' : 'form', 'value' : kw}
    
    @validate(validators=get_form, error_handler=test)
    @expose()
    def validation(self, *args, **kw):
        print 'validation'
        raise redirect(url('test'))