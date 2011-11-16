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
from pygdv.model import DBSession, Project, Species, Sequence, Track, User, Group
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