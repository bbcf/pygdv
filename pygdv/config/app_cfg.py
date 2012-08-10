# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in pygdv.

This file complements development/deployment.ini.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::
    
    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))
 
"""

from tg.configuration import AppConfig

import pygdv
from pygdv import model
from pygdv.lib import app_globals, helpers 
import tg

base_config = AppConfig()
base_config.renderers = []


base_config.package = pygdv

#Enable json in expose
base_config.renderers.append('json')
#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')

# if you want raw speed and have installed chameleon.genshi
# you should try to use this renderer instead.
# warning: for the moment chameleon does not handle i18n translations
#base_config.renderers.append('chameleon_genshi')
#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = model
base_config.DBSession = model.DBSession
base_config.use_transaction_manager=True


base_config.use_toscawidgets=True
base_config.use_toscawidgets2=True




# HOOKS
def on_startup():
    import datetime
    print ' --- starting application --- '+str(datetime.datetime.now())
    if tg.config.get('plugin.service.url') is None:
        print 'WARNING : YOU MUST SET THE "plugin.service.url" in your config file.'

    if tg.config.get('plugin.shared.key') is None:
        print 'WARNING : YOU MUST SET THE "plugin.shared.key" in your config file.'

def on_shutdown():
    print '--- stopping application --- '
base_config.call_on_startup = [on_startup]
base_config.call_on_shutdown = [on_shutdown]


token = 'GDV'











