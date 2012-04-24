from tw import forms as twf
from tw.forms import validators as twv
from pygdv.widgets.plugins import validators as gdvv
from tg import tmpl_context


def get_track_in_form():
    '''
    Method to put in options in a 'select' field to get the current tracks of the project in the form
    '''
    return [(track.id, track.name) for track in tmpl_context.tracks]



class ThresholdForm(twf.TableForm):

    submit_text = 'Submit job' # text of the submit button
    hover_help = True              # show help_text with mouse onHover
    show_errors = True             # show red labels when validators failed
    fields = [                     # define the fields you need in your form
              twf.HiddenField('_private_params'),                          # field needed to transfert information to the validation system
             
              
              twf.SingleSelectField(id='track', label_text='Track : ',    # simple 'select' field with a custom validator
              help_text = 'Select the track to apply the threshold on.', options=get_track_in_form, 
              validator=gdvv.TrackValidator(datatype='signal', not_empty=True)),
              
              twf.Spacer(),                                                # a spacer between two field
              
              twf.TextField(label_text='Threshold', id='thr',              # a simple input field (with a simple validator)
                            help_text = 'Input the trhreshold here', validator=twv.NotEmpty()),
              ]

class ImageForm(twf.TableForm):

    submit_text = 'Compute image'            # text of the submit button
    hover_help = True              # show help_text with mouse onHover
    show_errors = True             # show red labels when validators failed
    fields = [                     # define the fields you need in your form
              twf.HiddenField('_private_params'),    # field needed to transfert information to the validation system
             
            twf.SingleSelectField(id='my_track', label_text='Track : ',    # simple 'select' field with a custom validator
              help_text = 'Select the most beautiful track you have.', options=get_track_in_form, 
              validator=gdvv.TrackValidator(datatype='features', not_empty=True)),
              
              twf.Spacer(),
              twf.CheckBox(id='per_chromosomes', label_text='Per chromosomes', help_text='Display a count per chromosomes'),
              ]
    

