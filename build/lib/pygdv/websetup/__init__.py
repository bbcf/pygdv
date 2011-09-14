# -*- coding: utf-8 -*-
"""Setup the pygdv application"""

import logging

from pygdv.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)

from schema import setup_schema
import bootstrap

def setup_app(command, conf, vars):
    """Place any commands to setup pygdv here"""
    print 'load environment'
    load_environment(conf.global_conf, conf.local_conf)
    print 'setup schema'
    setup_schema(command, conf, vars)
    print 'bootstrap'
    bootstrap.bootstrap(command, conf, vars)
