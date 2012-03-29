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
    ('Output', 'output_display'),
    ('Status', lambda obj: get_job_status(obj)),
    ('Action', lambda obj:genshi.Markup(
        '<a href="%s"> result </a> '
        % url('./result', params={'id' : obj.id})
         + get_delete_link(obj.id, constants.full_rights)
        ))
])

def get_job_status(job=None):
    '''
    Get a output for the status of a task : a link to the traceback if the status is ``FAILURE``,
    else the string representing the status.
    @param track : the track to get the status from
    '''
    obj = job
    if obj.status != constants.ERROR: return obj.status
    return genshi.Markup('<a href="%s">%s</a>' % (url('./traceback', params={'id':obj.id}),
                                                  constants.ERROR
                                                  ))
    
    
    
    
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
