"""Track Controller"""

from pygdv.lib.base import BaseController
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import not_anonymous, has_any_permission

from tg import expose, flash, require, request, tmpl_context, validate, request
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate,with_trailing_slash

from pygdv.model import DBSession, Track, Input, TrackParameters, Sequence, Task, Project
from pygdv.widgets.track import track_table, track_export, track_table_filler, track_new_form, track_edit_filler, track_edit_form, track_grid
from pygdv import handler
from pygdv.lib import util, constants
import os
import transaction
from pygdv.lib import checker, reply


__all__ = ['TrackController']


class TrackController(CrudRestController):
    allow_only = has_any_permission(constants.perm_user, constants.perm_admin)
    model = Track
    table = track_table
    table_filler = track_table_filler
    edit_form = track_edit_form
    new_form = track_new_form
    edit_filler = track_edit_filler

   
    @expose('json')
    def all(self, *args, **kw):
        user=handler.user.get_user_in_session(request)
        return dict(tracks=user.tracks)


    
    
    @with_trailing_slash
    @expose('pygdv.templates.list')
    @expose('json')
    #@paginate('items', items_per_page=10)
    def get_all(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        data = [util.to_datagrid(track_grid, user.tracks, "Track Listing", len(user.tracks)>0)]
        return dict(page='tracks', model='track', form_title="new track",items=data,value=kw)
    
    
    
    @require(not_anonymous())
    @expose('pygdv.templates.form')
    def new(self, *args, **kw):
        tmpl_context.widget = track_new_form
        return dict(page='tracks', value=kw, title='new Track')
    

    @expose('json')
    def create(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        files = util.upload(**kw)
        
        if files is None:
            return reply.error(request, 'No file to upload.', './', {})
            
        if not 'assembly' in kw:
            return reply.error(request, 'Missing assembly parameters.', './', {})
        track_ids = []
        
        if not files :
            return reply.error(request, 'No file to upload.', './', {})
        project = None
        if 'project_id' in kw:
            project = DBSession.query(Project).filter(Project.id == kw['project_id']).first()
            if project is None:
                return reply.error(request, 'Project with id %s not found.' % kw['project_id'], './', {})
            
        for filename, f in files:
            sequence = DBSession.query(Sequence).filter(Sequence.id == kw['assembly']).first()
            task_id, track_id = handler.track.create_track(user.id, sequence, f=f.name, trackname=filename, project=project)
            
            if task_id == constants.NOT_SUPPORTED_DATATYPE or task_id == constants.NOT_DETERMINED_DATATYPE:
                return reply.error(request, task_id, './', {})
            track_ids.append(track_id)
             
        transaction.commit()
        return reply.normal(request, 'Track(s) successfully uploaded.', './', {'track_ids' : track_ids})  
    
    @expose('json')
    @validate(track_new_form, error_handler=new)
    def post(self, *args, **kw):
        raise self.create(*args, **kw) 
    

    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        id = args[0]
        for track in user.tracks :
            if int(id) == track.id :
                return CrudRestController.post_delete(self, *args, **kw)
        flash("You haven't the right to delete any tracks which is not yours")
        raise redirect('./')
    
    
    @expose('tgext.crud.templates.edit')
    def edit(self, *args, **kw):
        return CrudRestController.edit(self, *args, **kw)
    
    @expose()
    @validate(track_edit_form, error_handler=edit)
    def put(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        id = args[0]
        for track in user.tracks :
            if int(id) == track.id :
                track = DBSession.query(Track).filter(Track.id == id).first()
                track.name = kw['name']
                DBSession.flush()
                redirect('../')
        
        flash("You haven't the right to edit any tracks which is not yours")
        raise redirect('../')
    
    @expose('pygdv.templates.track_export')
    def export(self, track_id, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.can_download_track(user.id, track_id):
            flash("You haven't the right to export any tracks which is not yours")
            raise redirect('../')
        track = DBSession.query(Track).filter(Track.id == track_id).first()
        
        data = util.to_datagrid(track_grid, [track])
        tmpl_context.form = track_export
        return dict(page='tracks', model='Track', info=data, form_title='', value=kw)
    
    @expose()
    def dump(self, *args, **kw):
        print args
        print kw
        pass
    
    @expose()
    def link(self, track_id, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_track(user.id, track_id):
            flash("You haven't the right to download any tracks which is not yours")
        
        raise redirect('./')
        return 'not implemented'
    
    @expose()
    def traceback(self, track_id):
        user = handler.user.get_user_in_session(request)
        print user
        if not checker.user_own_track(user.id, track_id):
            flash("You haven't the right to look at any tracks which is not yours")
            raise redirect('./')
        track = DBSession.query(Track).filter(Track.id == track_id).first()
        print track
        return track.traceback
    
    
