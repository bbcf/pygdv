from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller, TableFiller
from pygdv.model import DBSession, Task
from tw.forms.validators import NotEmpty
import tw.forms as twf
import genshi
from tg import url





# TABLE
class GTable(TableBase):
    __model__ = Task
    __omit_fields__ = ['result']
    
   
   
# TABLE FILLER
class GTableFiller(TableFiller):
    __model__ = Task
   
# NEW
class NewGForm(AddRecordForm):
    __model__ = Task

# EDIT
class GEditForm(EditableForm):
    __model__ = Task

# EDIT FILLER
class GEditFiller(EditFormFiller):
    __model__ = Task




task_grid = twf.DataGrid(fields=[
    ('Id', 'id'),
    ('Task id', 'task_id'),
    ('Status', 'status'),
    ('Date', 'date_done'),
    ('Traceback', 'traceback'),
    ('Action', lambda obj:genshi.Markup(
        '<a href="%s">get result</a> '
        % (
           url('./get_result', params=dict(id=obj.id))
           ) 
        ))
])



celerytask_table = GTable(DBSession)
celerytask_table_filler = GTableFiller(DBSession)
celerytask_new_form = NewGForm(DBSession)
celerytask_edit_form = GEditForm(DBSession)
celerytask_edit_filler = GEditFiller(DBSession)
