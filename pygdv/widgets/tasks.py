from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller, TableFiller
from pygdv.model import DBSession, CeleryTask
from tw.forms.validators import NotEmpty
import tw.forms as twf







# TABLE
class GTable(TableBase):
    __model__ = CeleryTask
    __omit_fields__ = ['result']
    
   
   
# TABLE FILLER
class GTableFiller(TableFiller):
    __model__ = CeleryTask
   
# NEW
class NewGForm(AddRecordForm):
    __model__ = CeleryTask

# EDIT
class GEditForm(EditableForm):
    __model__ = CeleryTask

# EDIT FILLER
class GEditFiller(EditFormFiller):
    __model__ = CeleryTask






celerytask_table = GTable(DBSession)
celerytask_table_filler = GTableFiller(DBSession)
celerytask_new_form = NewGForm(DBSession)
celerytask_edit_form = GEditForm(DBSession)
celerytask_edit_filler = GEditFiller(DBSession)
