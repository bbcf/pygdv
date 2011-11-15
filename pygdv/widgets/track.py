from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller, TableFiller


import tw.forms as twf
import tw.dynforms as twd
import genshi

from tg import url

from pygdv.model import DBSession, Track, Species, Sequence
from pygdv.lib.helpers import get_delete_link, get_edit_link, get_task_status, get_export_link
from pygdv.lib import constants


# TABLE
class TTable(TableBase):
    __model__ = Track
    __omit_fields__ = ['_created']
    
# TABLE FILLER
class TTableFiller(TableFiller):
    __model__ = Track
   
# NEW
class NewTForm(AddRecordForm):
    __model__ = Track
    __base_widget_args__ = {'hover_help': True}

# EDIT
class TEditForm(EditableForm):
    __model__ = Track
    __limit_fields__ = ['name']

# EDIT FILLER
class TEditFiller(EditFormFiller):
    __model__ = Track


        
track_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    ('Created', 'created'),
    ('Assembly', 'sequence'),
    ('Type', 'vizu'),
    ('Status', lambda obj: get_task_status(obj)),
    ('Action', lambda obj:genshi.Markup(
        '<div class=actions>'
        + get_export_link(obj.id, rights = constants.full_rights)                               
        + get_delete_link(obj.id, rights = constants.full_rights)
        + get_edit_link(obj.id, rights = constants.full_rights)
        + '</div>'
        ))
])
track_in_project_grid = track_grid


#twf.DataGrid(fields=[
#    ('Name', 'name'),
#    ('Type', 'vizu'),
#    ('Action', lambda obj:genshi.Markup(
#     '<a href="%s">download</a> <a href="%s">link</a> '
#        % (
#           url('/tracks/download', params=dict(track_id=obj.id)),
#           url('./link', params=dict(track_id=obj.id))
#           ) 
##        + get_remove_link(obj.id) 
##        + get_copy_link(obj.id)
#        ))
#])




def get_species():
        species = DBSession.query(Species).all()
        return [(sp.id,sp.name) for sp in species]   

def get_assemblies(species):
    if species and species[0] and species[0]:
        nr_assemblies = DBSession.query(Sequence).join(Species).filter(Sequence.species_id == species[0][0]).all()
        return [(nr.id,nr.name) for nr in nr_assemblies]
    return []

class UploadFrom(twf.TableForm):

    submit_text = 'Upload a file'
    hover_help = True
    show_errors = True
    action='post'
    species = get_species()
    nr_assemblies = get_assemblies(species)
    fields = [
              
    twf.FileField(label_text='Select a file in your computer ',id='file_upload',
    help_text = 'Browse the file to upload in your computer. It will be converted to a Track.'),
    twf.TextArea(id='urls',label_text='Or enter url(s) to access your file(s)',
                          help_text = 'You can enter multiple urls separated by space or "enter".'),
   twd.CascadingSingleSelectField(id='species', label_text='Species : ',options=get_species,
help_text = 'Choose the species',cascadeurl='/sequences/get_nr_assemblies_from_species_id'),
  twf.Spacer(),
    twf.SingleSelectField(id='nr_assembly', label_text='Assembly : ',options=nr_assemblies,
help_text = 'Choose the assembly.'),
  twf.Spacer(),
              ]
    def update_params(self, d):
        super(UploadFrom,self).update_params(d)
        species=get_species()
        d['species']=species
        d['nr_assembly']=get_assemblies(species)
        return d


#def get_import_file_form(project_id):
#    return ImportFile('import_file_form',action='upload',value={'project_id':project_id})
#
#
#
#import_file_form = ImportFile('import_file_form',action='upload')
class TrackExport(twf.TableForm):
    submit_text = 'Download'
    hover_help = True
    show_errors = True
    action='dump'
    fields = [
            twf.HiddenField('track_id'),
            twf.SingleSelectField(id='format', label_text='Format : ', help_text='select the output format', options=constants.formats_export)
              ]
    
track_export = TrackExport()
track_table = TTable(DBSession)
track_table_filler = TTableFiller(DBSession)
track_new_form = UploadFrom('upload_form',action='post')
track_edit_form = TEditForm(DBSession)
track_edit_filler = TEditFiller(DBSession)
