from tw import forms as twf
from tw.forms import validators as twv
from pygdv.widgets.plugins import validators as gdvv
from tg import url

class ExampleForm(twf.TableForm):

    submit_text = 'This is a test' # text of the submit button
    hover_help = True              # show help_text with mouse onHover
    show_errors = True             # show red labels when validators failed
    fields = [                     # define the fields you need in your form
              twf.HiddenField('_plugin_name'),                                                                  # field needed to transfert information to the validation system
              twf.TextField(label_text='Simple textfield', id='text',                                            # a simple input field
                            help_text = 'This is some additional help.'),
              twf.Spacer(),                                                                                     # a spacer between two field
              twf.TextField(label_text='Simple textfield that must not be empty', id='text_not_empty',           # a textfield with a simple validator (this field must be filled)
                            help_text = '', validator=twv.NotEmpty()),
              twf.Spacer(),                                                                                     # a spacer between two field
              twf.TextArea(label_text='Drop tracks here', id='signal_track',
              help_text='Here put one signal track', validator=gdvv.TrackValidator(datatype='signal'))
              ]



