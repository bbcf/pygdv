'''
Permission widgets.
'''

from sprox.tablebase import TableBase
from sprox.dojo.tablebase import DojoTableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import TableFiller, EditFormFiller
from sprox.dojo.fillerbase import DojoTableFiller
from sprox.dojo.formbase import DojoEditableForm 

from pygdv.model import DBSession, Permission



# TABLE
class PTable(TableBase):
    __model__ = Permission
    
# TABLE FILLER
class PTableFiller(TableFiller):
    __model__ = Permission
    
# NEW
class NewPForm(AddRecordForm):
    __model__ = Permission

# EDIT
class PEditForm(DojoEditableForm):
    __model__ = Permission
   
# EDIT FILLER
class PEditFiller(EditFormFiller):
    __model__ = Permission






perm_table = PTable(DBSession)
perm_table_filler = PTableFiller(DBSession)
perm_new_form = NewPForm(DBSession)
perm_edit_form = PEditForm(DBSession)
perm_edit_filler = PEditFiller(DBSession)