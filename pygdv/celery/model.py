# -*- coding: utf-8 -*-

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import tg
from sqlalchemy import create_engine
from celery.conf import conf
from pygdv.lib import constants
        


def init_model(url):
    engine = create_engine(url, echo=False)
    Session = sessionmaker(autoflush=False, autocommit=False, bind = engine)
    #  extension=ZopeTransactionExtension(), bind=engine)
    return Session




def init_plugins():
    '''
    Init the plugin manager
    WARNING : celery daemon MUST run on the same server because of the plugins :
    plugins are identified by python hash method which differ between computers. 
    If you want to put celery on another server, replace hash() method by the haslib module.
    '''
    from yapsy.PluginManager import PluginManager
    manager = PluginManager()
    manager.setPluginPlaces([constants.plugin_directory()])
    manager.collectPlugins()
    return manager  




# Import your model modules here.
from pygdv.model.constants import *
from pygdv.model.database import Project, Sequence, Job
from pygdv.model.auth import User



DBSession = init_model(conf['BROKER_HOST'])


Manager = init_plugins()