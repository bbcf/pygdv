import tw2.forms as twf
import tw2.core as twc
import tw2.dynforms as twd

import tw.forms as oldtwf
import tw.dynforms as oldtwd
from pygdv.model import DBSession, Species, Sequence
from tg import url

# circle
class AddUser(twf.TableForm):
    cid = twf.HiddenField()
    mail = twf.TextField(
        label='e-mail : ',
        help_text = 'Enter the user e-mail.',
        validator=twc.EmailValidator(required=True))
    submit = twf.SubmitButton(id="submit", value="Add")


class NewCircle(twf.TableForm):
    name = twf.TextField(label='Name : ',
        help_text="Enter the circle's name",
        validator=twc.Validator(required=True))

    description = twf.TextField(label='Description : ',
        help_text="Enter the circle's description",
        validator=twc.Validator(required=True)
    )
    submit = twf.SubmitButton(id="submit", value="New")



# track
class EditTrack(twf.TableForm):
    color = twf.HiddenField()
    track_id = twf.HiddenField()
    name = twf.TextField(label='Name : ',
        help_text="Enter the track's name",
        validator=twc.Validator(required=True))
    submit = twf.SubmitButton(id="submit", value="Edit")


# project
class EditProject(twf.TableForm):
    pid = twf.HiddenField()
    name = twf.TextField(label='Name : ', validator=twc.Validator(required=True))
    tracks = twf.MultipleSelectField(label='Tracks : ', css_class='track_select')
    submit = twf.SubmitButton(id="submit", value="Edit")

class ShareProject(twf.TableForm):
    pid = twf.HiddenField()
    circles = twf.MultipleSelectField(label='Circles : ', css_class='circle_select')
    submit = twf.SubmitButton(id="submit", value="Share")


def get_species():
        species = DBSession.query(Species).all()
        return [(sp.id,sp.name) for sp in species]   

def get_assemblies(species):
    if species and species[0] and species[0]:
        assemblies = DBSession.query(Sequence).join(Species).filter(Sequence.species_id == species[0][0]).all()
        return [(nr.id,nr.name) for nr in assemblies]
    return []

class NewProject(oldtwf.TableForm):
    submit_text = 'New project'
    hover_help = True
    show_errors = True
    action='post'
    species = get_species()
    assemblies = get_assemblies(species)
    fields = [
              oldtwf.TextField(label_text='Name',id='name',
                            help_text = 'Give a name to your project', validator=oldtwf.validators.NotEmpty),
              oldtwd.CascadingSingleSelectField(id='species', label_text='Species : ',options=get_species,
            help_text = 'Choose the species', cascadeurl=url('/sequences/get_assemblies_from_species_id')),
              oldtwf.Spacer(),
                oldtwf.SingleSelectField(id='assembly', label_text='Assembly : ',options=assemblies,
            help_text = 'Choose the assembly.'),
              ]
    
                  
    def update_params(self, d):
        super(NewProject,self).update_params(d)
        species=get_species()
        d['species']=species
        d['assembly']=get_assemblies(species)
        return d

    print species
#            print sequences
#            mapp = {}
#            fields = []
#            for sp in species:
#                seqs = []
#                for seq in sequences:
#                    if seq.species_id == sp.id:
#                        seqs.append((seq.id, seq.name))
#                mapp[sp.name] = seqs
#            import tw2.forms as twf2
#            import tw2.dynforms as twd
#            mapping = {}
#            for k, v in mapp.iteritems():
#                transform_k = k.replace(' ', '_').lower()
#                mapping[k] = [transform_k]
#
#                tmp_field = twf2.SingleSelectField(id=transform_k, label="assembly", options=v, prompt_text=None)
#                fields.append(tmp_field)
#
#
#            fields.append(twf2.HiddenField(id='project_id'))
#            fields.append(twf2.HiddenField(id='meth'))
#            fields.insert(0, twd.HidingSingleSelectField(id='species', label_text='Species : ',options=[(sp.id, sp.name) for sp in species], mapping=mapping, prompt_text=None))
#            fields.insert(0, twf2.FileField(id='file_upload', label='Upload : ', help_text='Upload file from filesystem'))
#            fields.insert(0, twf2.TextField(id='url', label='Url : ', help_text='Provide an url'))
#            upload_track = twf2.TableForm(children=fields).req()


def new_project(action=None):
    species = DBSession.query(Species).all()
    mapping = {}
    fields = []
    for sp in species:
        key_name = sp.name.replace(' ', '_').lower()
        mapping[sp.name] = [key_name]
        opts = [(seq.id, seq.name) for seq in sp.sequences]
        fields.append(twf.SingleSelectField(id=key_name, label="assembly", options=opts, prompt_text=None))
    print mapping
    fields.insert(0,  twd.HidingSingleSelectField(id='species', label_text='Species : ',
        options=[(sp.id, sp.name) for sp in species], mapping=mapping, prompt_text=None))
    fields.insert(0, twf.TextField(id='name', label='Name : ', validator=twc.Validator(required=True)))

    return twf.TableForm(children=fields, action=action)


class MultipleFileUpload(twd.GrowingGridLayout):
    f = twf.FileField()
    more = twf.CheckBox()

class TestForm(twf.TableForm):
    file_field = MultipleFileUpload()
    submit = twf.SubmitButton(id="submit", value="Share")



class NewTrack(twf.TableForm):
    file_upload = twf.FileField(label='Upload : ', help_text='Upload file from filesystem')
    url = twf.TextField(label='Url : ', help_text='Provide an url') 
    species = twd.HidingSingleSelectField(label_text='Species : ',
                                          help_text = 'Choose species : ')
    meth = twf.HiddenField()

class NewTrack2(twf.TableForm):
    project_id = twf.HiddenField()
    file_upload = twf.FileField(label='Upload : ', help_text='Upload file from filesystem')
    url = twf.TextField(label='Url : ', help_text='Provide an url') 


