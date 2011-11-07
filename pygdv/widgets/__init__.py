# -*- coding: utf-8 -*-
"""The widget package contains all widgets (tables, form, ... needed for the project)"""
from pygdv.lib import constants




class ModelWithRight(object):
    '''
    Generic class to dynamically add right of viewing on a model object.
    '''
    
    def __init__(self, obj, rights):
        self.dec = obj
        self.rights = rights
