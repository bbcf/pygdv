from tw import forms as twf
from tw.forms import validators as twv
from tg import url

class ExampleForm(twf.TableForm):

    submit_text = 'This is a test' # text of the submit button
    hover_help = True              # show help_text with mouse onHover
    show_errors = True             # show red labels when validators failed
    fields = [
              twf.HiddenField('_plugin_name'),
              twf.TextField(label_text='Simple textfield',id='text',
                            help_text = 'This is some additional help.'),
              twf.Spacer(),
              twf.TextField(label_text='Simple textfield that must not be empty',id='text_not_empty',
                            help_text = '', validator=twv.NotEmpty()),
              ]


exampleform = ExampleForm()

