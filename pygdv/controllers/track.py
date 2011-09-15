"""User Controller"""
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import not_anonymous, has_any_permission

from tg import expose, flash, require, request, tmpl_context
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate,with_trailing_slash

from pygdv.model import DBSession, Track
from pygdv.widgets.track import track_table, track_table_filler, track_new_form, track_edit_filler, track_edit_form, track_grid
from pygdv import handler

import os
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
        data = [handler.util.to_datagrid(track_grid, user.tracks, "Track list", len(user.tracks)>0)]
        return dict(page='track', model='track', form_title="new track",items=data,value=kw)
    

    @expose('genshi:tgext.crud.templates.post_delete')
    def post_delete(self, *args, **kw):
        flash("You haven't the right to delete any tracks")
        redirect('/tracks')
    
    
    
    @expose('tgext.crud.templates.edit')
    def edit(self, *args, **kw):
        flash("You haven't the right to edit any tracks")
        redirect('/tracks')
    
    
    
    @require(not_anonymous())
    @expose('genshi:tgext.crud.templates.new')
    def new(self, *args, **kw):
        return super(TrackController, self).new(*args, **kw)
   
    @expose()
    @registered_validate(error_handler=new)
    def post(self, *args, **kw):
        del kw['sprox_id']
        print kw
        user = handler.user.get_user_in_session(request)
        files = handler.util.upload(file_upload=kw['file_upload'], urls=kw['urls'], url=None, fsys=None, fsys_list=None)
        if files is not None:
            for filename, file in files:
                handler.track.create_track(user.id, file=file, trackname=filename)
    
    
    @expose()
    @registered_validate(error_handler=edit)
    def put(self, *args, **kw):
       
        pass
    
    
    
#    @require(not_anonymous())
#    @expose('gdvpy.templates.upload_form')
#    def upload_form(self, **kw):
#        '''
#        An upload from.
#        '''
#        # get user
#        user = handler.user.get_user_in_session(request)
#        tmpl_context.form = import_file_form
#        return dict(page='import file', title="Import a file" ,value=kw, project_id=project_id)
#    
#    
#    @validate(import_file_form, error_handler=upload_form)
#    @expose()
#    @require(not_anonymous())
#    def upload(self, **kw):
#        '''
#        Upload a file
#        '''
#        user =  user_ctl.get_user_in_session(request)
#        if not user :
#            flash("Cannot import : user not logged")
#            redirect("upload_form")
#        if not 'project_id' in kw :
#            flash("Upload must be linked to a project")
#            redirect("upload_form")
#        
#        project_id=kw['project_id']
#        # parse parameters
#        if 'file_upload' in kw:
#            filename = kw['file_upload'].filename
#            file_value = kw['file_upload'].value
#        
#        if 'urls' in kw:
#            pass
#        
#       
#        # get a tmp directory
#        tmp = util.get_unique_tmp_directory()
#        # write the file in
#        file_path = os.path.join(tmp,filename)
#        f = file(file_path, "w")
#        f.write(file_value)
#        f.close()
#        
#        flash("Upload successful.")
#        redirect(url('detail',params=dict(project_id=project_id)))
        
        