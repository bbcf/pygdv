from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller, TableFiller
from pygdv.model import DBSession, Right
from tw.forms.validators import NotEmpty
import tw.forms as twf


class RTable(TableBase):
    __model__ = Right
    
class RTableFiller(TableFiller):
    __model__ = Right
   
class NewForm(AddRecordForm):
    __model__ = Right

class EditForm(EditableForm):
    __model__ = Right
class EditFiller(EditFormFiller):
    __model__ = Right






right_table = RTable(DBSession)
right_table_filler = RTableFiller(DBSession)
right_new_form = NewForm(DBSession)
right_edit_form = EditForm(DBSession)
right_edit_filler = EditFiller(DBSession)
