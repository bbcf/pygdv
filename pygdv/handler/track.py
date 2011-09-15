'''
Tracks handler.
'''
from pygdv.model import DBSession, Input, Track
import os
from pygdv.model import constants
from pygdv.lib import util
import transaction

def create_track(user_id, trackname=None, file=None):
    '''
    Create track from files :
    
    create input : can exist or not
    create track
    
    @param trackname : name to give to the track
    @param file : the file
    '''
    print 'creating track'
    if file is not None:
        input = create_input(file)
        track = Track()
        if trackname is not None:
            track.name = trackname
        track.visu = constants.NOT_DETERMINED_DATATYPE
        track.user_id = user_id
        track.input_id = input.id
        DBSession.add(track)
        transaction.commit()
    
   
    
    
    
    
    

def create_input(file):
    
    '''
    Create an input if it's new, or simply return the id of an already inputed file 
    @param file : the file
    @return : an Input
    '''
    print 'creating input'
    sha1 = util.get_file_sha1(os.path.abspath(file.name))
    print "getting sha1 %s" % sha1
    transaction.begin()
    input = DBSession.query(Input).filter(Input.sha1 == sha1).first()
    if input is not None: 
        print "file already exist"
    else :
        print "new input"
        input = Input()
        input.sha1 = sha1
        DBSession.add(input)
        #PROCESS INPUT
        print 'TODO : processing input'
        
    transaction.commit()
    return input   
        
        
        
        
         