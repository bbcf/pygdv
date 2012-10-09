from pygdv.lib.base import BaseController


from repoze.what.predicates import has_permission
from tg import expose, flash, request, url, abort
from tg.controllers import redirect
import json
from pygdv.model import DBSession, Sequence, Species, Group
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

    @expose('pygdv.templates.sequence_edit')
    def edit(self, *args, **kw):
        user = handler.user.get_user_in_session(request)

        # get circle id
        if request.method == 'GET':
            sequence_id = args[0]
        else :
            sequence_id = kw.get('cid')

        sequence_id=int(sequence_id)
        sequence = DBSession.query(Sequence).filter(Sequence.id == sequence_id).first()
        if not sequence:
            abort(404, 'Sequence with id %s not found' % sequence_id)

        if not sequence.public:
            add_user_widget = form.AddUser(action=url('/sequences/edit/%s' % sequence_id)).req()

            if request.method == 'POST':
                # add an user
                mail = kw.get('mail')
                try:
                    add_user_widget.validate({'cid' : sequence_id, 'mail' : mail})
                except twc.ValidationError as e:
                    users = ', '.join(['%s' % u.email for u in sequence.users])
                    default_tracks = ', '.join(['%s' % t.name for t in sequence.default_tracks])
                    kw['cid'] = sequence_id
                    widget = e.widget
                    widget.value = kw
                    return dict(page='sequences', users=users, add_user_widget=widget, default_tracks=default_tracks, au_error=True, seq_id=sequence_id)

                to_add = DBSession.query(User).filter(User.email == mail).first()
                if to_add is None:
                    to_add = handler.user.create_tmp_user(mail)
                sequence.users.append(to_add)
                DBSession.flush()

            kw['cid'] = sequence_id
            add_user_widget.value = kw

        else:
            add_user_widget = None

        users = ['%s' % u.email for u in sequence.users]
        default_tracks = ['%s' % t.name for t in sequence.default_tracks]


        return dict(page='sequences', users=users, add_user_widget=add_user_widget, default_tracks=default_tracks, au_error=False, seq_id=sequence_id)


    @expose('pygdv.templates.sequence_add')
    def add(self, *args, **kw):

        sequence_id = int(args[0])
        value = {}
        new_form = form.NewTrackSequence(action=url('/tracks/create')).req()
        value['sequence_id'] = sequence_id
        value['track_admin'] = True
        new_form.value = value
        return dict(page='sequences', widget=new_form, seq_id=sequence_id)

