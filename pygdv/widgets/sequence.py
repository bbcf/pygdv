from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.dojo.formbase import DojoEditableForm
from sprox.fillerbase import EditFormFiller, TableFiller
import tw.forms as twf, tw.dynforms as twd
from sprox.widgets import PropertyMultipleSelectField
import genshi
from tg import app_globals as gl
from tg import url
from pygdv.handler import genrep
from pygdv.model import DBSession, Sequence, Track, Group, User



# TABLE
class STable(TableBase):
    __model__ = Sequence
    __omit_fields__ = ['_created']
    
# TABLE FILLER
class STableFiller(TableFiller):
    __model__ = Sequence
   
# NEW
class SSNewForm(AddRecordForm):
    __model__ = Sequence
    __base_widget_args__ = {'hover_help': True}
    __limit_fields__ = ['name']
# EDIT

    
# EDIT FILLER
class SEditFiller(EditFormFiller):
    __model__ = Sequence
   

def get_species():
        species = genrep.get_species()
        return [(sp.id,sp.species) for sp in species]   

def get_assemblies(species):
        if species and species[0] and species[0][0]:
            assemblies = genrep.get_assemblies_not_created_from_species_id(species[0][0])
            return [(nr.id, nr.name) for nr in assemblies]
        return []
    

class SNewForm(twf.TableForm):
    submit_text = 'Create sequence'
    hover_help = True
    show_errors = True
    species = get_species()
    assemblies = get_assemblies(species)
    fields = [
              twf.Spacer(),
              twd.CascadingSingleSelectField(id='species', label_text='Species : ',options=species,
            help_text = 'Choose the species',cascadeurl=url('/sequences/get_assemblies_not_created_from_species_id')),
              twf.Spacer(),
                twf.SingleSelectField(id='assembly', label_text='Assembly : ',options=assemblies,
            help_text = 'Choose the assembly.'),
              twf.Spacer()
              ]
     
    def update_params(self,d):
        super(SNewForm,self).update_params(d)
        species=get_species()
        d['species']=species
        d['assembly']=get_assemblies(species)
        return d
    
    
class AdminTracksField(PropertyMultipleSelectField):
    def _my_update_params(self, d, nullable=False):
        tracks = DBSession.query(Track).join(User).join(User.groups).filter(Group.name == gl.group_admins).all()
        options = [(track.id, '%s (%s)'%(track.name, track.id))
                            for track in tracks ]
        d['options']= options
        return d
    
class SEditForm(DojoEditableForm):
    __model__ = Sequence
    __field_order__ = ['default_tracks', 'name']
    default_tracks = AdminTracksField


sequence_table = STable(DBSession)
sequence_table_filler = STableFiller(DBSession)
sequence_new_form = SNewForm()
sequence_edit_form = SEditForm(DBSession)
sequence_edit_filler = SEditFiller(DBSession)
