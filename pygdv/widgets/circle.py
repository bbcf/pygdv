from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.dojo.formbase import DojoEditableForm
from sprox.fillerbase import EditFormFiller, TableFiller
import tw.forms as twf, tw.dynforms as twd
from tw.forms.validators import Int, NotEmpty
from sprox.widgets import PropertyMultipleSelectField
import genshi
from tg import app_globals as gl
from sprox.widgets.dojo import SproxDojoSelectShuttleField, SproxDojoSortedSelectShuttleField
from tg import url, tmpl_context
from pygdv.handler import genrep
from pygdv.model import DBSession, Circle, Track, Group, User



# TABLE
class STable(TableBase):
    __model__ = Circle
    __omit_fields__ = ['_created','creator_id','id', 'Admin']
    __field_order__ = ['name', 'description', 'users']
    
# TABLE FILLER
class STableFiller(TableFiller):
    __model__ = Circle
    def users(self, circle):
        return ', '.join([user.short() for user in circle.users])

# NEW
class SSNewForm(AddRecordForm):
    __model__ = Circle
    __base_widget_args__ = {'hover_help': True}
    
# EDIT
def get_users():
    return [(user.id, user.__unicode__()) for user in DBSession.query(User).all()]

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
    
def get_circle_name():
    return tmpl_context.circle.name

def get_circle_description():
    return tmpl_context.circle.description

def get_users():
    return [(user.id, user.__unicode__()) for user in DBSession.query(User).all()]

class UserSelectField(SproxDojoSelectShuttleField):
    def _my_update_params(self, d, nullable=False):
        d['options']=get_users()
        return d
    
class EditCircleForm(DojoEditableForm):
    __model__ = Circle
    __base_widget_args__ = {'hover_help': True,'submit_text':'Edit project','show_errors':True}
    __limit_fields__ = ['name', 'description', 'users']
    __field_order__ = ['name', 'description', 'users']
    __require_fields__ = ['name', 'description', 'users']
    
    twf.HiddenField('_method')
    name = twf.TextField(label_text='Name',id='name',
                            help_text = 'edit the name', validator=NotEmpty, default=get_circle_name)
    
    description = twf.TextArea(id='description', label_text='Description : ',validator=NotEmpty, 
                               default=get_circle_description,
                               help_text='edit the description')
    
    users = UserSelectField
    

    
class SEditForm(DojoEditableForm):
    __model__ = Circle
    __omit_fields__ = ['creator_id', 'id']


from pygdv.lib import constants
from pygdv.lib.helpers import get_delete_link, get_circles_edit_link

circle_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    ('Description', 'description'),
    ('Owner', 'creator'),
    ('Members', 'get_users'),
    ('Action', lambda obj:genshi.Markup(
        '<div class=actions>'
        + get_delete_link(obj.id, rights = constants.full_rights)
        + get_circles_edit_link(obj.id)
        + '</div>'
        ))  
])






circle_table = STable(DBSession)
circle_table_filler = STableFiller(DBSession)
circle_new_form = CNewForm()
circle_edit_form = EditCircleForm(DBSession)
circle_edit_filler = SEditFiller(DBSession)
