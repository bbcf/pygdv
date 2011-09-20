from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller, TableFiller
from sprox.widgets import PropertyMultipleSelectField
from tw.api import WidgetsList

import tw.forms as twf,tw.dynforms as twd
import genshi
from tw.forms.validators import Int, NotEmpty
from tg import url, tmpl_context

from pygdv.model import DBSession, Project, Species, Sequence, Track, User, Group
from pygdv.lib.helpers import get_delete_link
from pygdv import handler


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

def get_circles_right():
    return [(circle_right.id) for circle_right in tmpl_context.circle_rights]
       
class NewProjectFrom(twf.TableForm):

    submit_text = 'New project'
    hover_help = True
    show_errors = True
    action='post'
    species = get_species()
    nr_assemblies = get_assemblies(species)
    tracks=[]
    fields = [
              twf.TextField(label_text='Name',id='name',
                            help_text = 'Give a name to your project', validator=NotEmpty),
              twd.CascadingSingleSelectField(id='species', label_text='Species : ',options=species,
            help_text = 'Choose the species',cascadeurl='/sequences/get_nr_assemblies_from_species_id'),
              twf.Spacer(),
                twf.SingleSelectField(id='nr_assembly', label_text='Assembly : ',options=nr_assemblies,
            help_text = 'Choose the assembly.'),
              twf.Spacer(),
            twf.MultipleSelectField(id='tracks', label_text='Tracks : ',options=get_tracks,
              help_text = 'Add tracks to the project'),
              twf.MultipleSelectField(id='circle_right', label_text="Circles with rights : ",options=get_circles_right,
                                      help_text="Choose group to share with")
              
]              
    def update_params(self, d):
        super(NewProjectFrom,self).update_params(d)
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
    ('Last access', 'last_access'),
    ('Type', 'visu'),
    ('Status', 'get_status'),
    ('Action', lambda obj:genshi.Markup(
        '<a href="%s">export</a> <a href="%s">link</a> '
        % (
           url('/projects/export', params=dict(project_id=obj.id)),
           url('/group/link', params=dict(project_id=obj.id))
           ) 
        + get_delete_link(obj.id) 
        ))
])





project_table = PTable(DBSession)
project_table_filler = PTableFiller(DBSession)
project_new_form = NewProjectFrom()
project_edit_form = PEditForm(DBSession)
project_edit_filler = PEditFiller(DBSession)
