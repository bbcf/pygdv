"""Sequence Controller"""
from tgext.crud import CrudRestController
from tgext.crud.decorators import registered_validate

from repoze.what.predicates import not_anonymous, has_any_permission, has_permission

from tg import expose, flash, require, request, tmpl_context, validate
from tg import app_globals as gl
from tg.controllers import redirect
from tg.decorators import paginate,with_trailing_slash, without_trailing_slash

from pygdv.model import DBSession, Sequence, Species
from pygdv.widgets.sequence import sequence_table, sequence_table_filler, sequence_new_form, sequence_edit_filler, sequence_edit_form
from pygdv import handler
from pygdv.lib import util

import transaction

__all__ = ['SequenceController']


class SequenceController(CrudRestController):
    allow_only = has_any_permission(gl.perm_user, gl.perm_admin)
    model = Sequence
    table = sequence_table
    table_filler = sequence_table_filler
    edit_form = sequence_edit_form
    new_form = sequence_new_form
    edit_filler = sequence_edit_filler

   
   
   
   
    @expose("json") 
    def get_nr_assemblies_not_created_from_species_id(self, value):
        '''
        Get the assemblies not created in GDV that are in Genrep
        '''
        nr_assemblies = handler.genrep.get_nr_assemblies_not_created_from_species_id(value)
        nr_assemblies = [(nr.id, nr.name) for nr in nr_assemblies]
        return {'nr_assembly':nr_assemblies}
    
    
    @expose("json") 
    def get_nr_assemblies_from_species_id(self, value):
        '''
        Get the assemblies created in GDV
        '''
        nr_assemblies = DBSession.query(Sequence).filter(Sequence.species_id == value).all()
        nr_assemblies = [(nr.id, nr.name) for nr in nr_assemblies]
        return {'nr_assembly':nr_assemblies}
    
    
    
    
    
    
#    
#    @with_trailing_slash
#    @expose('pygdv.templates.list')
#    @expose('json')
#    #@paginate('items', items_per_page=10)
#    def get_all(self, *args, **kw):
#        user = handler.user.get_user_in_session(request)
#        data = [util.to_datagrid(sequence_grid, user.sequences, "Sequence list", len(user.sequences)>0)]
#        return dict(page='sequence', model='sequence', form_title="new sequence",items=data,value=kw)
#    
#    
#    
#    @require(not_anonymous())
#    @expose('pygdv.templates.form')
#    def new(self, *args, **kw):
#        tmpl_context.widget = sequence_new_form
#        return dict(page='sequences', value=kw, title='new Track')
#    
#    
#
#    @expose('genshi:tgext.crud.templates.post_delete')
#    def post_delete(self, *args, **kw):
#        user = handler.user.get_user_in_session(request)
#        id = args[0]
#        for sequence in user.sequences :
#            if int(id) == sequence.id :
#                return CrudRestController.post_delete(self, *args, **kw)
#        flash("You haven't the right to delete any sequences which is not yours")
#        raise redirect('./')
#    
#    
#    
#    @expose('tgext.crud.templates.edit')
#    def edit(self, *args, **kw):
#        flash("You haven't the right to edit any sequences")
#        raise redirect('./')
#    
#    
#    
#  
#  
    @without_trailing_slash
    @require(has_permission('admin', msg='Only for admins'))
    @expose('tgext.crud.templates.new')
    def new(self, *args, **kw):
        return CrudRestController.new(self, *args, **kw)
    
    @expose()
    @require(has_permission('admin', msg='Only for admins'))
    @validate(sequence_new_form, error_handler=new)
    def post(self, *args, **kw):
        species_id = kw['species']
        nr_assembly_id = kw['nr_assembly']
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
        if not DBSession.query(Sequence).filter(Sequence.id == nr_assembly_id).first():
            nr_assembly = handler.genrep.get_nr_assembly_by_id(nr_assembly_id)
            seq = Sequence()
            seq.id = nr_assembly_id
            seq.name = nr_assembly.name
            seq.species_id = species_id
            DBSession.add(seq)
            DBSession.flush()
            seq = DBSession.query(Sequence).filter(Sequence.id == nr_assembly_id).first()
            handler.sequence.add_new_sequence(seq)
            flash( '''Sequence created: %s'''%( seq ))
        transaction.commit()
        raise redirect("./")
        
   
#    @with_trailing_slash
#    @expose('tgext.crud.templates.get_all')
#    @expose('json')
#    @paginate('value_list', items_per_page=7)
#    def get_all(self, *args, **kw):
#        return CrudRestController.get_all(self, *args, **kw)

   
  
    
#    
#    @expose()
#    @registered_validate(error_handler=edit)
#    def put(self, *args, **kw):
#        pass
        