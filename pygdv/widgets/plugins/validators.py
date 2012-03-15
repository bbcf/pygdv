import formencode, track
from pygdv.model import DBSession, Track


class TrackValidator(formencode.api.FancyValidator):
    '''
    Validate a track datatype.
    ex : TrackValidator(datatype='signal')
    '''
    datatype = 'features' # datatype of a track
    not_empty = False     # if the field can be empty
    
    messages = { 'dt' : 'Wrong track datatype : %(dt)s.',
        }                       # messages to give to user if validation fail
    
    def _to_python(self, value, state):
        '''
        This method convert the form input to be 
        understandable by python code.
        Convert the track id to the track path
        '''
        track = DBSession.query(Track).filter(Track.id == value).first()
        return track.path

    def validate_python(self, value, state):
        '''
        Actual method which validate the input.
        '''
        with track.load(value, 'sql', readonly=True) as t:
            if not t.datatype == self.datatype:
                raise formencode.Invalid(self.message('dt', state, dt='signal'), value, state)
        

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
        
        