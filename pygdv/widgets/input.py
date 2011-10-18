from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller, TableFiller
from pygdv.model import DBSession, Input
from tw.forms.validators import NotEmpty
import tw.forms as twf
import genshi
from tg import url





# TABLE
class ITable(TableBase):
    __model__ = Input
    __omit_fields__ = ['result']
    
   
   
# TABLE FILLER
class ITableFiller(TableFiller):
    __model__ = Input
   
# NEW
class NewIForm(AddRecordForm):
    __model__ = Input

# EDIT
class IEditForm(EditableForm):
    __model__ = Input

# EDIT FILLER
class IEditFiller(EditFormFiller):
    __model__ = Input






input_table = ITable(DBSession)
input_table_filler = ITableFiller(DBSession)
input_new_form = NewIForm(DBSession)
input_edit_form = IEditForm(DBSession)
input_edit_filler = IEditFiller(DBSession)
