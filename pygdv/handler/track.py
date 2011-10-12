from __future__ import absolute_import
'''
Tracks handler.
'''

from pygdv.model import DBSession, Input, Track, InputParameters, Task
import os, shutil
from pygdv.model import constants
from pygdv.lib import util
from pygdv.celery import tasks


from track.util import determine_format
from pygdv.model import constants



#extension = guess_file_format('/tmp/asdkljasdklj')
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
        input = create_input(file,trackname)
        track = Track()
        if trackname is not None:
            track.name = trackname
        track.sequence_id = sequence_id
        track.user_id = user_id
        track.input_id = input.id
        DBSession.add(track)
        DBSession.flush()
   
    
    
    
    
    

def create_input(file, trackname):
    
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
        
        
        file_path = os.path.abspath(file.name)
        print 'Processing input %s' % file_path
        out_dir = util.get_directory('tracks_dir', sha1)
        print 'to %s : ' % out_dir
        
        
        format = determine_format(file_path)
        print 'gessing format : %s' % format
        
        datatype = _formats.get(format, constants.NOT_DETERMINED_DATATYPE)
        datatype = constants.SIGNAL
        
        print 'gessing datatype %s' % datatype
        input.datatype = datatype
       
        print input
        
        dispatch = _process_dispatch.get(format,lambda *args, **kw : not_recognized(*args, **kw))
        
        print 'dispatch %s' % dispatch
        if trackname is None:
            trackname = file.name
            
        async_result = dispatch(datatype=datatype, path=file_path, sha1=sha1, name=trackname)
        task = DBSession.query(Task).filter(Task.task_id == async_result.task_id).first()
        
        input.task_id = task.id
        
        DBSession.add(input)
        print 'deleting temporary file'
        os.remove(os.path.abspath(file.name))
        
    DBSession.flush()
    return input   












_process_dispatch = {'sql' : lambda *args, **kw : process_database(*args, **kw),
                    'bed' : lambda *args, **kw : not_impl(*args, **kw),
                    'bigWig' : lambda *args, **kw : not_impl(*args, **kw),
                    'wig' : lambda *args, **kw : not_impl(*args, **kw),
                    'bedgraph' : lambda *args, **kw : not_impl(*args, **kw)}


_formats = {'sql' : constants.NOT_DETERMINED_DATATYPE,
                    'bed' : constants,
                    'bigWig' : lambda *args, **kw : not_impl(*args, **kw),
                    'wig' : lambda *args, **kw : not_impl(*args, **kw),
                    'bedgraph' : lambda *args, **kw : not_impl(*args, **kw)
                    }



def process_database(datatype, path, sha1, name):
    '''
    Process the input as a SQLite database already build by the ``track`` package.
    @param datatype : the ``datatype`` of the file.
    @param path : the path of the database
    @param sha1 : the sha1 of the file
    @param name : the name of the track
    @return the task associated
    '''
    
    
    return _sql_dispatch.get(datatype, lambda *args, **kw : not_recognized(*args, **kw))(path,sha1)


_sql_dispatch = {'quantitative' : lambda *args, **kw : _signal(*args, **kw),
                 constants.SIGNAL : lambda *args, **kw : _signal(*args, **kw),
                 
                 'qualitative' :  lambda *args, **kw : _features(*args, **kw),
                 constants.FEATURES :  lambda *args, **kw : _features(*args, **kw),
                 
                 'extended' :  lambda *args, **kw : _relationnal(*args, **kw),
                  constants.RELATIONAL :  lambda *args, **kw : _relationnal(*args, **kw)
                 }



def _signal(path, sha1):
    '''
    Process a ``signal`` database.
    @return the task associated
    '''
    return tasks.process_signal.delay(path, sha1)

def _features(path, sha1, name):
    '''
    Process a ``feature`` database.
    @return the task associated
    '''
    tasks.process_features.delay(path, sha1, name, False)

def _relationnal(path, sha1, name):
    '''
    Process a ``relationnal`` database
    @return the task associated
    '''
    tasks.process_features.delay(path, sha1, name, True)
    


def not_recognized(datatype=None, **kw):
    '''
    Format not recognized
    '''
    pass

def not_impl():
    raise NotImplementedError

