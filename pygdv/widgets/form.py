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
        help_text='Enter the user e-mail.',
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
    pid = twf.HiddenField()
    track_id = twf.HiddenField()
    name = twf.TextField(label='Name : ',
        help_text="Enter the track's name",
        validator=twc.Validator(required=True))
    submit = twf.SubmitButton(id="submit", value="Edit")


class ShareProject(twf.TableForm):
    pid = twf.HiddenField()
    circles = twf.MultipleSelectField(label='Circles : ', css_class='circle_select')
    submit = twf.SubmitButton(id="submit", value="Share")


def get_species():
        species = DBSession.query(Species).all()
        return [(sp.id, sp.name) for sp in species]


def get_assemblies(species):
    if species and species[0] and species[0]:
        assemblies = DBSession.query(Sequence).join(Species).filter(Sequence.species_id == species[0][0]).all()
        return [(nr.id, nr.name) for nr in assemblies]
    return []


class MultipleFileUpload(twd.GrowingGridLayout):
    f = twf.FileField()
    more = twf.CheckBox()


class NewTrack(twf.TableForm):
    file_upload = twf.FileField(label='Upload : ', help_text='Upload file from filesystem')
    url = twf.TextField(label='Url : ', help_text='Provide an url')
    smapping = twf.HiddenField()
    trackname = twf.TextField(label='Name : ')
    extension = twf.TextField(label='Extension : ', help_text="Specify the extension of your file if it's not already provided by your file name.")
    species = twf.SingleSelectField(label='Species :')
    assembly = twf.SingleSelectField(label='Assembly :', options=[])
    submit = twf.SubmitButton(id="submit", value="New")


class NewTrackPrefilled(twf.TableForm):
    file_upload = twf.FileField(label='Upload : ', help_text='Upload file from filesystem')
    url = twf.TextField(label='Url : ', help_text='Provide an url')
    trackname = twf.TextField(label='Name : ')
    extension = twf.TextField(label='Extension : ', help_text="Specify the extension of your file if it's not already provided by your file name.")
    project_id = twf.HiddenField()
    submit = twf.SubmitButton(id="submit", value="New")


class NewTrackSequence(twf.TableForm):
    file_upload = twf.FileField(label='Upload : ', help_text='Upload file from filesystem')
    url = twf.TextField(label='Url : ', help_text='Provide an url')
    sequence_id = twf.HiddenField()
    track_admin = twf.HiddenField()
    submit = twf.SubmitButton(id="submit", value="New")


    # project
class EditProject(twf.TableForm):
    pid = twf.HiddenField()
    name = twf.TextField(label='Name : ', validator=twc.Validator(required=True))
    tracks = twf.MultipleSelectField(label='Tracks : ', css_class='track_select')
    submit = twf.SubmitButton(id="submit", value="Edit")


class NewProject(twf.TableForm):
    smapping = twf.HiddenField()
    name = twf.TextField(label='Name')
    species = twf.SingleSelectField(label='Species : ')
    assembly = twf.SingleSelectField(label='Assembly :', options=[])
    submit = twf.SubmitButton(id="submit", value="New")


class NewSequenceForm(twf.ListForm):
    smapping = twf.HiddenField()
    species = twf.SingleSelectField(label='Species : ', options=[])
    assembly = twf.SingleSelectField(label='Assembly :', options=[])
    submit = twf.SubmitButton(id="submit", value="New")
