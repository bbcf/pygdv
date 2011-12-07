from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller, TableFiller
from sprox.widgets import PropertyMultipleSelectField
from tw.api import WidgetsList
from sqlalchemy import and_
from tw.api import Widget
import tw.forms as twf,tw.dynforms as twd
import tw
import genshi
from tw.forms.validators import Int, NotEmpty
from tg import url, tmpl_context
from sprox.dojo.formbase import DojoEditableForm
from sprox.widgets.dojo import SproxDojoSelectShuttleField, SproxDojoSortedSelectShuttleField
from pygdv.model import DBSession, Project, Species, Sequence, Track, User, Group, Job
from pygdv.lib.helpers import get_delete_link, get_detail_link, get_edit_link, get_project_right_sharing_form, get_view_link, get_share_link
from pygdv import handler
from tg import app_globals as gl
from pygdv.lib import constants
from pygdv.widgets import SortableColumn




job_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    ('Description', 'description'),
    ('Output', 'output'),
    ('Status', 'status'),
    ('Action', lambda obj:genshi.Markup(
        '<a href="%s"> result </a> '
        % url('./result', params={'id' : obj.id})
        ))
])

# TABLE
class JobTable(TableBase):
    __model__ = Job
#    __omit_fields__ = ['_created']

# TABLE FILLER
class JobTableFiller(TableFiller):
    __model__ = Job
   
# NEW
class JobNewForm(AddRecordForm):
    __model__ = Job
#    __base_widget_args__ = {'hover_help': True}
#    __limit_fields__ = ['name']
    

# EDIT
class JobEditForm(EditableForm):
    __model__ = Job

# EDIT FILLER
class JobEditFiller(EditFormFiller):
    __model__ = Job

    
       

job_table = JobTable(DBSession)
job_table_filler = JobTableFiller(DBSession)
job_new_form = JobNewForm(DBSession)
job_edit_form = JobEditForm(DBSession)
job_edit_filler = JobEditFiller(DBSession)
