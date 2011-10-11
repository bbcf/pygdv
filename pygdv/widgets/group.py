from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller, TableFiller
from pygdv.model import DBSession, Group
from tw.forms.validators import NotEmpty
import tw.forms as twf







# TABLE
class GTable(TableBase):
    __model__ = Group
    __omit_fields__ = ['_created']
    
# TABLE FILLER
class GTableFiller(TableFiller):
    __model__ = Group
   
# NEW
class NewGForm(AddRecordForm):
    __model__ = Group
    __limit_fields__ = ['name', 'permissions', 'users']
    __field_order__ = ['name', 'permissions', 'users']
    __require_fields__ = ['name', 'permissions']
    __base_widget_args__ = {'hover_help': True}
    __dropdown_field_names__ = ['name', 'name']
    name = twf.TextField('name', validator=NotEmpty,
            help_text='Enter the name of the group you want to create.')

# EDIT
class GEditForm(EditableForm):
    __model__ = Group
    __limit_fields__ = ['name', 'permissions', 'users']
    __field_order__ = ['name', 'permissions', 'users']
    __require_fields__ = ['name', 'permissions']
    __base_widget_args__ = {'hover_help': True}
    
    name = twf.TextField('name', validator=NotEmpty,
            help_text='Modify the name of the group.')
   

# EDIT FILLER
class GEditFiller(EditFormFiller):
    __model__ = Group






group_table = GTable(DBSession)
group_table_filler = GTableFiller(DBSession)
new_group_form = NewGForm(DBSession)
group_edit_form = GEditForm(DBSession)
group_edit_filler = GEditFiller(DBSession)
