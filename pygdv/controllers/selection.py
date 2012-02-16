# -*- coding: utf-8 -*-
"""Error controller"""

from tg import request, expose, require
from bbcflib.genrep import GenRep, Assembly
from repoze.what.predicates import has_any_permission
from pygdv.lib import constants
from pygdv.model import DBSession, Selection, Location

__all__ = ['SelectionController']

chunk = 20000

class SelectionController(object):
  
  
    @expose()
    @require(has_any_permission(constants.perm_user, constants.perm_admin))
    def index(self):
        return ''
        
        
        
    @expose()
    @require(has_any_permission(constants.perm_user, constants.perm_admin))
    def save(self, project_id, color, description, locations):
        print "save %s, color %s, desc %s loc %s" % (project_id, color, description, locations)
        selection = Selection()
        selection.project_id = project_id
        selection.description = description
        selection.color = color
        DBSession.add(selection)
        DBSession.flush()
        
        for loc in locations:
            print loc
            obj = Location()
            obj.chromosome = loc['chr'] 
            obj.start = loc['start'] 
            obj.end = loc['end'] 
            obj.description = loc['desc'] 
            obj.selection = selection
            DBSession.add(obj)
        DBSession.flush()
        return 1

