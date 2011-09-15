'''
Tracks handler.
'''
from pygdv.model import DBSession, Input, Track
import os
import transaction
from pygdv.model import constants

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
        
       
        
    
   
    
    
    
    
    

def create_input(file):
    from pygdv import handler
    '''
    Create an input if it's new, or simply return the id of an already inputed file 
    @param file : the file
    @return : an Input
    '''
    print 'creating input'
    sha1 = handler.util.get_file_sha1(os.path.abspath(file.name))
    print "getting sha1 %s" % sha1
    input = DBSession.query(Input).filter(Input.sha1 == sha1).first()
    if input is not None: 
        print "file already exist"
        return input
    else :
        print "creating input"
        input = Input()
        input.sha1 = sha1
        DBSession.add(input)
        transaction.commit()
        
        #PROCESS INPUT
        print 'TODO : processing input'
        
        return input
       
        
        
        
        
         