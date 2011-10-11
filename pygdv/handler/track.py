'''
Tracks handler.
'''
from pygdv.model import DBSession, Input, Track, InputParameters
import os, shutil
from pygdv.model import constants
from pygdv.lib import util

def create_track(user_id, sequence_id, trackname=None, file=None):
    '''
    Create track from files :
    
        create input 
        create track from input
    
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
        track.sequence_id = sequence_id
        track.user_id = user_id
        track.input_id = input.id
        DBSession.add(track)
        DBSession.flush()
   
    
    
    
    
    

def create_input(file):
    
    '''
    Create an input if it's new, or simply return the id of an already inputed file 
    @param file : the file
    @return : an Input
    '''
    print 'creating input'
    sha1 = util.get_file_sha1(os.path.abspath(file.name))
    print "getting sha1 %s" % sha1
    input = DBSession.query(Input).filter(Input.sha1 == sha1).first()
    if input is not None: 
        print "file already exist"
    else :
        params = InputParameters()
        DBSession.add(params)
        DBSession.flush()
        
        input = Input()
        input.sha1 = sha1
        input.parameters = params
        DBSession.add(input)
       
        # process input
        print 'Processing input %s' % os.path.abspath(file.name)
        out_dir = util.get_directory('tracks_dir', sha1)
        print 'to %s : ' % out_dir
        
        #TODO : launch the task on Celery
         
        print 'deleting file'
        os.remove(os.path.abspath(file.name))
        
    DBSession.flush()
    return input   
        
        
        
        
         