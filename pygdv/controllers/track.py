"""Track Controller"""

from pygdv.lib.base import BaseController
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import not_anonymous, has_any_permission, has_permission

from tg import expose, flash, require, request, tmpl_context, validate, request
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate,with_trailing_slash

from pygdv.model import DBSession, Track, Input, TrackParameters, Sequence, Task, Project
from pygdv.widgets.track import track_table, track_export, track_table_filler, track_new_form, track_edit_filler, track_edit_form, track_grid, default_track_form
from pygdv import handler
from pygdv.lib import util, constants, checker, reply
import os
import transaction
from pygdv.celery import tasks
import pickle

__all__ = ['TrackController']


class TrackController(CrudRestController):
    allow_only = has_any_permission(constants.perm_user, constants.perm_admin)
    model = Track
    table = track_table
    table_filler = track_table_filler
    edit_form = track_edit_form
    new_form = track_new_form
    edit_filler = track_edit_filler

   
    @require(has_permission('admin', msg='Only for admins'))
    @expose('pygdv.templates.list')
    def all(self, *args, **kw):
        tracks = DBSession.query(Track).all()
        data = [util.to_datagrid(track_grid, tracks, "Track Listing", len(tracks)>0)]
        return dict(page='tracks', model='track', form_title="new track",items=data,value=kw)


    
    
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
        util.file_upload_converter(kw)
        
        task = tasks.process_track.delay(user.id, **kw)
        
        return reply.normal(request, 'Task launched.', './', {'task_id' : task.task_id})  
    
    @expose('json')
    @validate(track_new_form, error_handler=new)
    def post(self, *args, **kw):
        raise self.create(*args, **kw) 
    

    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        _id = args[0]
        
        if not checker.can_edit_track(user, _id) and not checker.user_is_admin(user.id):
            flash("You haven't the right to edit any tracks which is not yours")
            raise redirect('../')
        
        handler.track.delete(_id)
        raise redirect('./')
    
    
    @expose('tgext.crud.templates.edit')
    def edit(self, *args, **kw):
        track = DBSession.query(Track).filter(Track.id == args[0]).first()
        tmpl_context.color = track.parameters.color
        return CrudRestController.edit(self, *args, **kw)
    
    @expose()
    @validate(track_edit_form, error_handler=edit)
    def put(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        _id = args[0]
        
        if not checker.can_edit_track(user, _id) and not checker.user_is_admin(user.id):
            flash("You haven't the right to edit any tracks which is not yours")
            raise redirect('../')
        
        track = DBSession.query(Track).filter(Track.id == _id).first()
        track.name = kw['name']
        if 'color' in kw:
            track.parameters.color = kw['color']
        DBSession.flush()
        redirect('../')
        
        
    
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
        return "You will be able to export the desired track in the format wanted. It's not implemented yet."
    
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
        if not checker.user_own_track(user.id, track_id):
            flash("You haven't the right to look at any tracks which is not yours")
            raise redirect('./')
        track = DBSession.query(Track).filter(Track.id == track_id).first()
        return track.traceback
    
    @expose()
    def copy(self, track_id):
        user = handler.user.get_user_in_session(request)
        if not checker.can_download_track(user.id, track_id):
            return reply.error(request, 'You have no right to copy this track in your profile.', './', {})
        t = DBSession.query(Track).filter(Track.id == track_id).first()
        if not t:
            return reply.error(request, 'No track with this id.', './', {})
        handler.track.copy_track(user.id, t)
        return reply.normal(request, 'Copy successfull', './', {})
    
    
    @require(has_permission('admin', msg='Only for admins'))
    @expose('pygdv.templates.form')
    def default_tracks(self, **kw):
        tmpl_context.widget = default_track_form
        return dict(page='tracks', value=kw, title='new default track (visible on all projects with the same assembly)')
    
    @expose()
    @require(has_permission('admin', msg='Only for admins'))
    @validate(default_track_form, error_handler=default_tracks)
    def default_tracks_upload(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        kw['admin'] = True
        util.file_upload_converter(kw)
        
        task_id = tasks.process_track.delay(user.id, **kw)
        return reply.normal(request, 'Task launched.', '/home', {'task_id' : task_id})  
    
    @require(has_permission('admin', msg='Only for admins'))
    @expose('pygdv.templates.list')
    def admin(self, **kw):
        sequences = DBSession.query(Sequence).all()
        tracks = []
        for sequence in sequences:
            tracks += sequence.default_tracks
        data = [util.to_datagrid(track_grid, tracks, "Track Listing", len(tracks)>0)]
        
        return dict(page='tracks', model='track', form_title="admin tracks",items=data,value=kw)
    
    
    
    