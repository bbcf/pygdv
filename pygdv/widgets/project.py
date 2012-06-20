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
from pygdv.lib.helpers import get_delete_link, get_detail_link, get_edit_link, get_project_right_sharing_form, get_view_link, get_share_link, get_copy_project_link
from pygdv import handler
from tg import app_globals as gl
from pygdv.lib import constants
from pygdv.widgets import SortableColumn

# TABLE
class PTable(TableBase):
    __model__ = Project
    __omit_fields__ = ['_created']
    
# TABLE FILLER
class PTableFiller(TableFiller):
    __model__ = Project
   
# NEW
class NewPForm(AddRecordForm):
    __model__ = Project
    __base_widget_args__ = {'hover_help': True}
    __limit_fields__ = ['name']
    




def get_species():
        species = DBSession.query(Species).all()
        return [(sp.id,sp.name) for sp in species]   

def get_assemblies(species):
    if species and species[0] and species[0]:
        assemblies = DBSession.query(Sequence).join(Species).filter(Sequence.species_id == species[0][0]).all()
        return [(nr.id,nr.name) for nr in assemblies]
    return []
    
def get_tracks():
    return [(track.id, track.name) for track in tmpl_context.tracks]

def get_circles():
    return [(circle.id, '%s (%s)' %(circle.name, circle.description)) for circle in tmpl_context.circles]



    


class NewProjectFrom(twf.TableForm):

    submit_text = 'New project'
    hover_help = True
    show_errors = True
    action='post'
    species = get_species()
    assemblies = get_assemblies(species)
    fields = [
              twf.TextField(label_text='Name',id='name',
                            help_text = 'Give a name to your project', validator=NotEmpty),
              twd.CascadingSingleSelectField(id='species', label_text='Species : ',options=get_species,
            help_text = 'Choose the species', cascadeurl=url('/sequences/get_assemblies_from_species_id')),
              twf.Spacer(),
                twf.SingleSelectField(id='assembly', label_text='Assembly : ',options=assemblies,
            help_text = 'Choose the assembly.'),
              ]
    
                  
    def update_params(self, d):
        super(NewProjectFrom,self).update_params(d)
        species=get_species()
        d['species']=species
        d['assembly']=get_assemblies(species)
        return d

def get_project_tracks():
    return [(track.id, track.name) for track in tmpl_context.project.tracks]

def get_project_circles():
    return [(circle.id, '%s (%s)' %(circle.name, circle.description)) for circle in tmpl_context.project.circles]

def get_project_name():
    return tmpl_context.project.name

def get_project_species():
    sp = tmpl_context.project.species
    species = DBSession.query(Species).filter(Species.id != sp.id).all()
    species.insert(0, sp)
    return [(sp.id,sp.name) for sp in species]

def get_project_assemblies():
    sp = tmpl_context.project.species
    seq = tmpl_context.project.sequence
    assemblies = DBSession.query(Sequence).join(Species).filter(
                                and_(Sequence.species_id == sp.id,
                                     Sequence.id != seq.id)).all()
    assemblies.insert(0, seq)
    return [(nr.id,nr.name) for nr in assemblies]
    
class EditProjectForm(twf.TableForm):
    submit_text = 'Edit project'
    hover_help = True
    show_errors = True
    action=url('./?_method=PUT')
    #action='../put'
#    assemblies = get_assemblies(species)
    fields = [
             # twf.HiddenField(id='_method'),
              twf.TextField(label_text='Name',id='name',
                            help_text = 'Give a name to your project', validator=NotEmpty, default=get_project_name),
              twd.CascadingSingleSelectField(id='species', label_text='Species : ',options=get_project_species,
            help_text = 'Choose the species',cascadeurl=url('/sequences/get_assemblies_from_species_id')),
              twf.Spacer(),
                twf.SingleSelectField(id='assembly', label_text='Assembly : ',options=get_project_assemblies,
            help_text = 'Choose the assembly.'),
              twf.Spacer(),
            twf.MultipleSelectField(id='tracks', label_text='Tracks : ',options=get_tracks,
              help_text = 'Add tracks to the project'),
             twf.MultipleSelectField(id='circles', label_text="Circles : ",options=get_circles,
                                      help_text="Add Circles to share with. Circle(s) selected will automatically see your project.")
              
              
]              
    def update_params(self, d):
        super(EditProjectForm,self).update_params(d)
        species=get_species()
        d['species']=species
        d['assembly']=get_assemblies(species)
        return d
    
    
    
class TracksSelectField(SproxDojoSelectShuttleField):
    def _my_update_params(self, d, nullable=False):
        d['options']=get_tracks()
        return d
class CircleSelectField(SproxDojoSelectShuttleField):
    size = 'circle_select_field'
    def _my_update_params(self, d, nullable=False):
        d['options']=get_circles()
        return d


    

# EDIT
class PEditForm(EditableForm):
    __model__ = Project

# EDIT FILLER
class PEditFiller(EditFormFiller):
    __model__ = Project



project_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    ('Created', 'created'),
    ('Assembly', 'assembly'),
    ('Circles', 'get_circle_with_right_display'),
    ('Tracks', 'get_tracks'),
    ('Action', lambda obj:genshi.Markup(
          '<div class="actions">'                              
        + get_view_link(obj.id, 'project_id', constants.full_rights)
        + get_share_link(obj.id, 'project_id', constants.full_rights) 
        + get_delete_link(obj.id, constants.full_rights) 
        + get_edit_link(obj.id, constants.full_rights)
        + get_detail_link(obj.id, 'project_id', constants.full_rights)
        + '</div>'
        ))
])

project_admin_grid = twf.DataGrid(fields=[
    ('Id', 'id'),
    ('Name', 'name'),
    ('User', 'user'),
    ('Created', 'created'),
    ('Assembly', 'assembly'),
    ('Circles', 'get_circle_with_right_display'),
    ('Tracks', 'get_tracks'),
    ('Action', lambda obj:genshi.Markup(
        get_view_link(obj.id, 'project_id', constants.full_rights)
        ))
])



project_grid_sharing = twf.DataGrid(fields=[
    ('Name', 'name'),
    ('Created', 'created'),
    ('Assembly', 'assembly'),
    ('Circles', 'get_circle_with_right_display'),
    ('Tracks', 'get_tracks'),
    ('Action', lambda obj:genshi.Markup(get_view_link(obj.id, 'project_id', constants.full_rights)
        + get_share_link(obj.id) 
        + get_delete_link(obj.id) 
        + get_edit_link(obj.id)
        + '<a href="%s">add track</a> '
        % url('./add_track', params=dict(project_id=obj.id))
        ))
])



project_with_right = twf.DataGrid(fields = [
    ('Name', 'dec.name'),
    ('Created', 'dec.created'),
    ('Assembly', 'dec.assembly'),
    ('Tracks', 'dec.get_tracks'),
    ('Action', lambda obj:genshi.Markup(
        '<div class="actions">'
        + get_view_link(obj.dec.id, 'project_id', obj.rights) 
        + get_share_link(obj.dec.id, 'project_id', obj.rights)
        + get_copy_project_link(obj.dec.id, obj.rights)
        + get_delete_link(obj.dec.id, obj.rights) 
        + get_edit_link(obj.dec.id, obj.rights)
        + get_detail_link(obj.dec.id, 'project_id', obj.rights)
        + '</div>'
        ))             
                                            
                                            
                                            ])

  
class ProjectSharingDataGrid(twf.DataGrid):
    sharing_project_js = tw.api.JSLink(modname='pygdv', filename='public/js/helpers.js')
    javascript=[sharing_project_js]
    
    


    
    
class RightSharingForm(twf.TableForm):
    submit_text = 'change rights'
    action=url('post_share')
    fields = [
              twf.HiddenField(id='circle_id'),
              twf.CheckBoxTable(id='rights_checkboxes', num_cols=3, options=['Read','Download','Upload'])
              ]
    
    
project_sharing_grid = ProjectSharingDataGrid(fields=[
    ('Circle', 'circle.display'),
    ('Rights', lambda obj:genshi.Markup(
                        get_project_right_sharing_form(obj)))
    #('Rights',RightSharingForm() )                           
#    ('Upload', lambda obj:genshi.Markup(
#                get_right_checkbok(obj, gl.right_upload))),
    ])

class AvailableCirclesForm(twf.TableForm):
    submit_text = 'Add a circle to share with'
    hover_help = True
    show_errors = True
    action=url('./post_share_add')

    fields = [
              twf.HiddenField('project_id'),
             twf.MultipleSelectField(id='circles', label_text="Circles : ",options=get_circles, validator=NotEmpty,
                                     help_text="Add Circles to share with. Circle(s) selected will automatically have the ``read`` permission'")
                          ]              
    
class AvailableTracksForm(twf.TableForm):
    submit_text = 'Add track(s) to the project'
    hover_help = True
    show_errors = True
    action=url('./add')

    fields = [
              twf.HiddenField('project_id'),
             twf.MultipleSelectField(id='tracks', label_text="Tracks : ",options=get_tracks, validator=NotEmpty,
                help_text="Add track(s) to the project by selecting them. You can select more the one by holding the Ctrl button.")
              ]         
def get_selected_tracks():
    return tmpl_context.selected_tracks
def get_test():
        return [( track.id, track.name) for track in tmpl_context.tracks] + [(track.id, track.name, {'selected' : True}) for track in tmpl_context.selected_tracks ]

class EditProjectForm2(DojoEditableForm):
    __model__ = Project
    __base_widget_args__ = {'hover_help': True,'submit_text':'Edit project','show_errors':True}
    __limit_fields__ = ['name', 'species', 'assembly']
    __field_order__ = ['name', 'species', 'assembly']
    __require_fields__ = ['name', 'species', 'assembly']
    
    twf.HiddenField('_method')
    id = twf.HiddenField('Id')
    name = twf.TextField(label_text='Name',id='name',
                            help_text = 'Give a name to your project', validator=NotEmpty, default=get_project_name)
#    species = twd.CascadingSingleSelectField(id='species', label_text='Species : ',options=get_project_species,
#            help_text = 'Choose the species',cascadeurl='/sequences/getassemblies_from_species_id')
#    assembly = twf.SingleSelectField(id='assembly', label_text='Assembly : ',options=get_project_assemblies,
#            help_text = 'Choose the assembly.')
    tracks = twf.MultipleSelectField(id='tracks', label_text='Tracks : ',options=get_test, value='selected',
             help_text="Add track(s) to the project by selecting them. You can select more the one by holding the Ctrl/Cmd button.")
    #tracks = TracksSelectField
    #_circle_right = CircleSelectField
    
    def _my_update_params(self, d, nullable=False):
        super(EditProjectForm,self).update_params(d)
        species=get_species()
        d['species']=species
        d['assembly']=get_assemblies(species)
        return d
    
       
project_table = PTable(DBSession)
project_table_filler = PTableFiller(DBSession)
project_new_form = NewProjectFrom()
project_edit_form = EditProjectForm2(DBSession)
project_edit_filler = PEditFiller(DBSession)
circles_available_form = AvailableCirclesForm()
tracks_available_form = AvailableTracksForm()