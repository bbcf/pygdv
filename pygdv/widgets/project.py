from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller, TableFiller

import tw.forms as twf
import genshi

from tg import url

from pygdv.model import DBSession, Project
from pygdv.lib.helpers import get_delete_link



# TABLE
class PTable(TableBase):
    __model__ = Project
    __omit_fields__ = ['_created']
    
# TABLE FILLER
class PTableFiller(TableFiller):
    __model__ = Project
   
# NEW
class NewPForm(AddRecordForm):
    __model__ = Project
    __base_widget_args__ = {'hover_help': True}

# EDIT
class PEditForm(EditableForm):
    __model__ = Project

# EDIT FILLER
class PEditFiller(EditFormFiller):
    __model__ = Project



project_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    ('Created', 'created'),
    ('Last access', 'last_access'),
    ('Type', 'visu'),
    ('Status', 'get_status'),
    ('Action', lambda obj:genshi.Markup(
        '<a href="%s">export</a> <a href="%s">link</a> '
        % (
           url('/projects/export', params=dict(project_id=obj.id)),
           url('/group/link', params=dict(project_id=obj.id))
           ) 
        + get_delete_link(obj.id) 
        ))
])





project_table = PTable(DBSession)
project_table_filler = PTableFiller(DBSession)
project_new_form = NewPForm(DBSession)
project_edit_form = PEditForm(DBSession)
project_edit_filler = PEditFiller(DBSession)
