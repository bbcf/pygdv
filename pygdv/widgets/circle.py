from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.dojo.formbase import DojoEditableForm
from sprox.fillerbase import EditFormFiller, TableFiller
import tw.forms as twf, tw.dynforms as twd
from tw.forms.validators import Int, NotEmpty
from sprox.widgets import PropertyMultipleSelectField
import genshi
from tg import app_globals as gl
from pygdv.handler import genrep
from pygdv.model import DBSession, Circle, Track, Group, User



# TABLE
class STable(TableBase):
    __model__ = Circle
    __omit_fields__ = ['_created']
    
# TABLE FILLER
class STableFiller(TableFiller):
    __model__ = Circle
   
# NEW
class SSNewForm(AddRecordForm):
    __model__ = Circle
    __base_widget_args__ = {'hover_help': True}
    
# EDIT
def get_users():
    return [(user.id, user.email) for user in DBSession.query(User).all()]

class CNewForm(twf.TableForm):
    submit_text = 'Create circle'
    hover_help = True
    show_errors = True
    fields = [
              twf.TextField(label_text='Name',id='name',
                            help_text = 'Give a name to circle', validator=NotEmpty),
              twf.Spacer(),
              twf.TextArea(label_text='Description',id='description',
                            help_text = 'Give a Descrition', validator=NotEmpty),
              twf.MultipleSelectField(id='users', label_text='Users : ',options=get_users,
              help_text = 'Add users to the circle'),
              twf.Spacer()
              ]
    
# EDIT FILLER
class SEditFiller(EditFormFiller):
    __model__ = Circle
   
   

    
class SEditForm(DojoEditableForm):
    __model__ = Circle
    __omit_fields__ = ['creator_id', 'id']

circle_table = STable(DBSession)
circle_table_filler = STableFiller(DBSession)
circle_new_form = CNewForm()
circle_edit_form = SEditForm(DBSession)
circle_edit_filler = SEditFiller(DBSession)
