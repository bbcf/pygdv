from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller, TableFiller


from pygdv.model import DBSession, User




# TABLE
class UTable(TableBase):
    __model__ = User
    __omit_fields__ = ['_created']
    
# TABLE FILLER
class UTableFiller(TableFiller):
    __model__ = User
   
# NEW
class NewUForm(AddRecordForm):
    __model__ = User
    __base_widget_args__ = {'hover_help': True}

# EDIT
class UEditForm(EditableForm):
    __model__ = User

# EDIT FILLER
class UEditFiller(EditFormFiller):
    __model__ = User










user_table = UTable(DBSession)
user_table_filler = UTableFiller(DBSession)
user_new_form = NewUForm(DBSession)
user_edit_form = UEditForm()
user_edit_filler = UEditFiller(DBSession)
