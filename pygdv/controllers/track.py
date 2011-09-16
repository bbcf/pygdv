"""Track Controller"""
from pygdv.lib.base import BaseController
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import not_anonymous, has_any_permission

from tg import expose, flash, require, request, tmpl_context, validate
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate,with_trailing_slash

from pygdv.model import DBSession, Track, Input, InputParameters
from pygdv.widgets.track import track_table, track_table_filler, track_new_form, track_edit_filler, track_edit_form, track_grid
from pygdv import handler
from pygdv.lib import util
import os
import transaction

__all__ = ['TrackController']


class TrackController(CrudRestController):
    allow_only = has_any_permission(gl.perm_user, gl.perm_admin)
    model = Track
    table = track_table
    table_filler = track_table_filler
    edit_form = track_edit_form
    new_form = track_new_form
    edit_filler = track_edit_filler

   
    
    @with_trailing_slash
    @expose('pygdv.templates.list')
    @expose('json')
    #@paginate('items', items_per_page=10)
    def get_all(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        data = [util.to_datagrid(track_grid, user.tracks, "Track list", len(user.tracks)>0)]
        return dict(page='tracks', model='track', form_title="new track",items=data,value=kw)
    
    
    
    @require(not_anonymous())
    @expose('pygdv.templates.form')
    def new(self, *args, **kw):
        tmpl_context.widget = track_new_form
        return dict(page='tracks', value=kw, title='new Track')
    
    

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
        flash("You haven't the right to edit any tracks")
        raise redirect('./')
    
    
    
  
   
    @expose()
    @validate(track_new_form, error_handler=new)
    def post(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        files = util.upload(**kw)
        if files is not None:
            for filename, file in files:
                handler.track.create_track(user.id, file=file, trackname=filename)
            transaction.commit()
            flash("Track(s) successfully uploaded.")
        else :
            flash("No file to upload.")
        raise redirect('./') 
        
    
#    @with_trailing_slash
#    @expose('tgext.crud.templates.get_all')
#    @expose('json')
#    @paginate('value_list', items_per_page=7)
#    def get_all(self, *args, **kw):
#        return CrudRestController.get_all(self, *args, **kw)

   
  
    
    
    @expose()
    @registered_validate(error_handler=edit)
    def put(self, *args, **kw):
        pass
        