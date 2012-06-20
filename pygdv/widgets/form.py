import tw2.forms as twf
import tw2.core as twc


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