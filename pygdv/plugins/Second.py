from pygdv.lib.plugin import OperationPlugin
from yapsy.IPlugin import IPlugin
from tw import forms as twf
from tw.forms import validators as twv
from pygdv.widgets.plugins import validators as gdvv


class SecondPlugin(IPlugin, OperationPlugin):
    
    
    
    def title(self):
        return 'My second example'
    
    def path(self):
        return ['Statistics', 'A sub category', 'a child']
    
    def output(self):
        return ExampleForm

    def process(self, **kw):
        return kw.get('param1', 0) + kw.get('param2', 0)


class ExampleForm(twf.TableForm):

    submit_text = 'Add'            # text of the submit button
    hover_help = True              # show help_text with mouse onHover
    show_errors = True             # show red labels when validators failed
    fields = [                     # define the fields you need in your form
              twf.HiddenField('form_id'),    # field needed to transfert information to the validation system
             
              twf.TextField(label_text='my param 1', id='param1',           # a simple input field
                            help_text = 'This is some additional help.'),
              
              twf.Spacer(),               # a spacer between two field
              
              twf.TextField(label_text='my param 2', id='param2',            # a textfield with a simple validator 
                            help_text = '', validator=twv.NotEmpty()),       # (this field must be filled)
              
              twf.Spacer(),        
              
              twf.TextArea(label_text='my signal track', id='signal_track',
              help_text='Here put one signal track',
               validator=gdvv.TrackValidator(datatype='signal', not_empty=True))  # a custom textfield (track drop container) 
                                                                                  # with a custom validator 
              ]
