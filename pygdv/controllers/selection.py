# -*- coding: utf-8 -*-
"""Error controller"""

from tg import request, expose, require, flash
from bbcflib.genrep import GenRep, Assembly
from repoze.what.predicates import has_any_permission
from pygdv.lib import constants, checker
from pygdv import handler
from pygdv.model import DBSession, Selection, Location
import json
from sqlalchemy.sql import and_, not_

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
        user = handler.user.get_user_in_session(request)
        if not checker.check_permission_project(user.id, project_id, constants.right_upload_id):
            flash('You must have %s permission to delete the project.' % constants.right_upload, 'error')
            return {'save' : 'failed'}
            
        print "save %s, color %s, desc %s loc %s" % (project_id, color, description, locations)
        ''' For the momenet, there is only one selection per project'''
        sel = DBSession.query(Selection).filter(Selection.project_id == project_id).first()
        if sel is None:
            sel = Selection()
            sel.project_id = project_id
            
        sel.description = description
        sel.color = color
        DBSession.add(sel)
        DBSession.flush()
        
        locations_ids = []
        # add locations
        
        for loc in json.loads(locations):
            obj = None
            if loc.has_key('id'):
                obj = DBSession.query(Location).join(Selection.locations).filter(
                        and_(Selection.id == sel.id, Location.id == loc.get('id'))).first()
                
            if obj is None:
                obj = Location()
                
            obj.chromosome = loc.get('chr') 
            obj.start = loc.get('start')
            obj.end = loc.get('end')
            obj.description = loc.get('desc', '') 
            obj.selection = sel
            DBSession.add(obj)
            DBSession.flush()
            locations_ids.append(obj.id)
        # remove not saved ones
        print locations_ids
        print DBSession.query(Location).all()
        print 'REMOVE'
        loc_toremove = DBSession.query(Location).filter(not_(Location.id.in_(locations_ids))).all()
        for l in loc_toremove:
            print l
            DBSession.delete(l)
        print 'REMOVE'
        DBSession.flush()
        print DBSession.query(Location).all()
        return {'saved' : 'ok'}
    
    
    
    @expose()
    @require(has_any_permission(constants.perm_user, constants.perm_admin))
    def delete(self, project_id, selection_id):
        user = handler.user.get_user_in_session(request)
        if not checker.check_permission_project(user.id, project_id, constants.right_upload_id):
            flash('You must have %s permission to delete the project.' % constants.right_upload, 'error')
            return {'delete' : 'failed'}
        selection = DBSession.query(Selection).filter(Selection.id == selection_id).first()
        if not selection.project_id == project_id:
            flash('Bad project_id : %s' % project_id, 'error')
            return {'delete' : 'failed'}
        DBSession.delete(selection)
        DBSession.flush()
        return {'delete' : 'success'}
    

