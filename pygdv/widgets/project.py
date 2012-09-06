import tw.forms as twf,tw.dynforms as twd
from pygdv.model import DBSession, Species, Sequence
from pygdv.lib.helpers import get_view_link
from pygdv.lib import constants
from tg import url
import genshi
from tw.forms.validators import Int, NotEmpty









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
def get_species():
    species = DBSession.query(Species).all()
    return [(sp.id,sp.name) for sp in species]

def get_assemblies(species):
    if species and species[0] and species[0]:
        assemblies = DBSession.query(Sequence).join(Species).filter(Sequence.species_id == species[0][0]).all()
        return [(nr.id,nr.name) for nr in assemblies]
    return []


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



project_new_form = NewProjectFrom()