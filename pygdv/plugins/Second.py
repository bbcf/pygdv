from pygdv.lib.plugin import OperationPlugin, new_track, get_project, get_sequence
from yapsy.IPlugin import IPlugin
from tw import forms as twf
from tw.forms import validators as twv
import formencode
import track, tempfile
 

# THE PLUGIN CODE

class SecondPlugin(IPlugin, OperationPlugin):
    
    
    
    def title(self):
        return 'My second example'
    
    def path(self):
        return ['Statistics', 'Simple operations', 'add two integers']
    
    def output(self):
        return ExampleForm

    def process(self, **kw):
        print kw
        result = int(kw.get('param1', 0)) + int(kw.get('param2', 0))
        
        # create a tmp file        
        _f = tempfile.NamedTemporaryFile(delete=True)
        fname = _f.name + '.sql'
        _f.close()
        
        # get parameters
        project_id = get_project(kw).id
        sequence_name = str(get_sequence(kw).name)
        
        # use them to process output
        with track.new(fname, 'sql') as t:
            t.write('1', ((10, 2000, result),), fields = ('start', 'end', 'score'))
            t.assembly = sequence_name
            t.datatype = 'signal'
        
        # create a new track on GDV
        new_track(kw, _file=fname, trackname='test plugin')




        
# A CUSTOM VALIDATOR                            
class MyIntegerValueValidator(formencode.api.FancyValidator):
    '''
    Validate my value with a specific test
    '''
    sup_limit = 10
    inf_limit = 0
    
    not_empty = False     # if the field can be empty
    
    messages = { 'er' : 'Value is out of boundaries : ' + str(inf_limit) + '< %(v)s. < '+ str(sup_limit),
        }                       # messages to give to user if validation fail
    
    def _to_python(self, value, state):
        '''
        This method convert the form input to be 
        understandable by python code.
        Convert the value to an integer
        '''
        return int(value)

    def validate_python(self, value, state):
        '''
        Actual method which validate the input.
        '''
        if value < self.inf_limit or value > self.sup_limit :
            raise formencode.Invalid(self.message('er', state, v=value), value, state)
        


# A CUSTOM FORM

class ExampleForm(twf.TableForm):

    submit_text = 'Add'            # text of the submit button
    hover_help = True              # show help_text with mouse onHover
    show_errors = True             # show red labels when validators failed
    fields = [                     # define the fields you need in your form
              twf.HiddenField('_private_params'),    # field needed to transfert information to the validation system
             
              twf.TextField(label_text='my param 1', id='param1',           # a simple input field
                            help_text = 'This is some additional help.', validator=twv.NotEmpty),
              
              twf.Spacer(),               # a spacer between two field
              
              twf.TextField(label_text='my param 2', id='param2',            # a textfield with a simple validator 
                            help_text = '', validator=MyIntegerValueValidator(sup_limit=100, not_empty=True)),       # (this field must be filled)
              
              twf.Spacer(),        
              
              twf.TextArea(label_text='my signal track', id='signal_track',
              help_text='Here put one signal track')  # a custom textfield (track drop container) 
              ]
    
    

    
    
    

                        