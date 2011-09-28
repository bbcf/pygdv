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

from pygdv.model import DBSession, Project, Species, Sequence, Track, User, Group
from pygdv.lib.helpers import get_delete_link, get_edit_link, get_project_right_sharing_form
from pygdv import handler
from tg import app_globals as gl


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
            nr_assemblies = DBSession.query(Sequence).join(Species).filter(Sequence.species_id == species[0][0]).all()
            return [(nr.id,nr.name) for nr in nr_assemblies]
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
    nr_assemblies = get_assemblies(species)
    fields = [
              twf.TextField(label_text='Name',id='name',
                            help_text = 'Give a name to your project', validator=NotEmpty),
              twd.CascadingSingleSelectField(id='species', label_text='Species : ',options=get_species,
            help_text = 'Choose the species',cascadeurl='/sequences/get_nr_assemblies_from_species_id'),
              twf.Spacer(),
                twf.SingleSelectField(id='nr_assembly', label_text='Assembly : ',options=nr_assemblies,
            help_text = 'Choose the assembly.'),
              twf.Spacer(),
            twf.MultipleSelectField(id='tracks', label_text='Tracks : ',options=get_tracks,
              help_text = 'Add tracks to the project'),
             twf.MultipleSelectField(id='circles', label_text="Circles : ",options=get_circles,
                                      help_text="Add Circles to share with. Circle(s) selected will automatically see your project.")
              
              
]              
    def update_params(self, d):
        super(NewProjectFrom,self).update_params(d)
        species=get_species()
        print species
        d['species']=species
        d['nr_assembly']=get_assemblies(species)
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

def get_project_nr_assemblies():
    sp = tmpl_context.project.species
    seq = tmpl_context.project.sequence
    nr_assemblies = DBSession.query(Sequence).join(Species).filter(
                                and_(Sequence.species_id == sp.id,
                                     Sequence.id != seq.id)).all()
    nr_assemblies.insert(0, seq)
    return [(nr.id,nr.name) for nr in nr_assemblies]
    
class EditProjectForm(twf.TableForm):
    submit_text = 'Edit project'
    hover_help = True
    show_errors = True
    action=url('./?_method=PUT')
    #action='../put'
#    nr_assemblies = get_assemblies(species)
    fields = [
             # twf.HiddenField(id='_method'),
              twf.TextField(label_text='Name',id='name',
                            help_text = 'Give a name to your project', validator=NotEmpty, default=get_project_name),
              twd.CascadingSingleSelectField(id='species', label_text='Species : ',options=get_project_species,
            help_text = 'Choose the species',cascadeurl='/sequences/get_nr_assemblies_from_species_id'),
              twf.Spacer(),
                twf.SingleSelectField(id='nr_assembly', label_text='Assembly : ',options=get_project_nr_assemblies,
            help_text = 'Choose the assembly.'),
              twf.Spacer(),
            twf.MultipleSelectField(id='tracks', label_text='Tracks : ',options=get_project_tracks,
              help_text = 'Add tracks to the project'),
             twf.MultipleSelectField(id='circles', label_text="Circles : ",options=get_project_circles,
                                      help_text="Add Circles to share with. Circle(s) selected will automatically see your project.")
              
              
]              
    def update_params(self, d):
        super(EditProjectForm,self).update_params(d)
        species=get_species()
        d['species']=species
        d['nr_assembly']=get_assemblies(species)
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
    ('Tracks', 'tracks'),
    ('Action', lambda obj:genshi.Markup(
        '<a href="%s">view</a> <a href="%s">share</a> '
        % (
           url('./view', params=dict(project_id=obj.id)),
           url('./share', params=dict(project_id=obj.id))
           ) 
        + get_delete_link(obj.id) 
        + get_edit_link(obj.id)
        ))
])


    
class ProjectSharingDataGrid(twf.DataGrid):
    sharing_project_js = tw.api.JSLink(modname='pygdv', filename='public/js/helpers.js')
    javascript=[sharing_project_js]
    
    
    
class RightSharingForm(twf.TableForm):
    submit_text = 'change rights'
    action='post_share'
    fields = [
              twf.HiddenField(id='cicle_id'),
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




project_table = PTable(DBSession)
project_table_filler = PTableFiller(DBSession)
project_new_form = NewProjectFrom()
project_edit_form = EditProjectForm()
project_edit_filler = PEditFiller(DBSession)
