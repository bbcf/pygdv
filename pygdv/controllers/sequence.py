from pygdv.lib.base import BaseController


from repoze.what.predicates import has_permission
from tg import expose, flash, request, url
from tg.controllers import redirect
import json
from pygdv.model import DBSession, Sequence, Species
from pygdv.widgets import datagrid, form
from pygdv.lib import constants, util
from pygdv.handler import genrep
from pygdv import handler

class SequenceController(BaseController):
    allow_only = has_permission(constants.perm_admin)


    @expose('pygdv.templates.sequences')
    def index(self, *args, **kw):

        seq_form = form.NewSequenceForm(action=url('/sequences')).req()
        species = genrep.get_species()

        m = {}
        sp_to_add = []
        for sp in species:
            assemblies = genrep.get_assemblies_not_created_from_species_id(sp.id)
            if len(assemblies) > 0:
                m[sp.id] = [(ass.id, ass.name) for ass in assemblies]
                sp_to_add.append(sp)
        sp_opts =  [(sp.id, sp.species) for sp in sp_to_add]
        seq_form.child.children[1].options = sp_opts
        value = {'smapping' : json.dumps(m)}
        seq_form.value = value
        grid = datagrid.sequences_grid


        if request.method == 'GET':
            sequences = DBSession.query(Sequence).all()
            seq_grid = [util.to_datagrid(grid, sequences, "Sequences", len(sequences)>0)]

            return dict(page="sequences", widget=seq_form, grid=seq_grid)
        else :
            species_id = kw['species']
            assembly_id = kw['assembly']
            # look if the species already exist in GDV, else create it
            species = DBSession.query(Species).filter(Species.id == species_id).first()
            if not species:
                species = handler.genrep.get_species_by_id(species_id)
                current_sp = Species()
                current_sp.id = species.id
                current_sp.name = species.species
                DBSession.add(current_sp)
                DBSession.flush()
                current_sp = DBSession.query(Species).filter(Species.id == species_id).first()
                flash( '''Species created: %s'''%( current_sp ))

            # look if the assembly not already created, else create it
            if not DBSession.query(Sequence).filter(Sequence.id == assembly_id).first():
                assembly = handler.genrep.get_assembly_by_id(assembly_id)
                seq = Sequence()
                seq.id = assembly_id
                seq.name = assembly.name
                seq.species_id = species_id
                DBSession.add(seq)
                DBSession.flush()
                seq = DBSession.query(Sequence).filter(Sequence.id == assembly_id).first()
                handler.sequence.add_new_sequence(seq)
                flash( '''Sequence created: %s'''%( seq ))
            DBSession.flush()
            sequences = DBSession.query(Sequence).all()
            seq_grid = [util.to_datagrid(grid, sequences, "Sequences", len(sequences)>0)]
            return dict(page="sequences", widget=seq_form, grid=seq_grid)