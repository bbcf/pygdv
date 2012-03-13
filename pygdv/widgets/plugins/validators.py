import formencode


class TrackValidator(formencode.api.FancyValidator):
    '''
    Validate a track datatype.
    ex : TrackValidator(datatype='signal')
    '''
    datatype = 'features' # datatype of a track
    not_empty = False     # if the field can be empty
    
    messages = { 'dt' : 'Wrong track datatype : %(dt)s.',
                 'overlapping' : 'You give a track with overlapping scores'
        }                       # messages to give to user if validation fail
    
    def _to_python(self, value, state):
        '''
        This method convert the form input to be 
        understandable by python code.
        Convert the path to a Track
        '''
        return value

    def validate_python(self, value, state):
        '''
        Actual method which validate the input.
        '''
        if True:
            raise formencode.Invalid(self.message('dt', state, dt='signal'), value, state)
        if False:
            raise formencode.Invalid(self.message('overlaping'))
        
    