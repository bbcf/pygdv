from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller, TableFiller

import tw.forms as twf
import genshi

from tg import url

from pygdv.model import DBSession, Track
from pygdv.lib.helpers import get_delete_link



# TABLE
class TTable(TableBase):
    __model__ = Track
    __omit_fields__ = ['_created']
    
# TABLE FILLER
class TTableFiller(TableFiller):
    __model__ = Track
   
# NEW
class NewTForm(AddRecordForm):
    __model__ = Track
    __base_widget_args__ = {'hover_help': True}

# EDIT
class TEditForm(EditableForm):
    __model__ = Track

# EDIT FILLER
class TEditFiller(EditFormFiller):
    __model__ = Track



track_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    ('Created', 'created'),
    ('Last access','last_access'),
    ('Type','vizu'),
    ('Action', lambda obj:genshi.Markup(
        '<a href="%s">export</a> <a href="%s">link</a> '+ get_delete_link(obj.id) 
        % (
           url('/tracks/export', params=dict(track_id=obj.id)),
           url('/group/link', params=dict(track_id=obj.id))
           )))
])





class UploadForm(AddRecordForm):
    __model__= Track
    submit_text = 'Upload a file'
    hover_help = True
    show_errors = True
    __limit_fields__ = []
    __field_order__ = ['upload_field', 'urls']
    __base_widget_args__ = {'hover_help': True, 'show_errors' : True, 'action'='post'}
    upload_field = twf.FileField(label_text='Select a file in your computer ',id='file_upload',
    help_text = 'Browse the file to upload in your computer. It will be converted to a Track.')
    urls =  twf.TextArea(id='urls',label_text='Or enter url(s) to access your file(s)',
                          help_text = 'You can enter multiple urls separated by space or "enter".')
    action='toto'


#def get_import_file_form(project_id):
#    return ImportFile('import_file_form',action='upload',value={'project_id':project_id})
#
#
#
#import_file_form = ImportFile('import_file_form',action='upload')


    

track_table = TTable(DBSession)
track_table_filler = TTableFiller(DBSession)
track_new_form = UploadForm(DBSession)
track_edit_form = TEditForm(DBSession)
track_edit_filler = TEditFiller(DBSession)
