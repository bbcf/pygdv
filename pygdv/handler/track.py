from __future__ import absolute_import
'''
Tracks handler.
'''

from pygdv.model import DBSession, Input, Track, TrackParameters, Task
import os, shutil
from pygdv.model import constants
from pygdv.lib import util
from pygdv.celery import tasks
from pygdv.lib.constants import track_directory
from track.util import determine_format
from pygdv.lib import constants



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
        
        
        params = TrackParameters()
        DBSession.add(params)
        DBSession.flush()
        
        track.parameters = params
        
        
        DBSession.add(track)
        DBSession.flush()
        
        params.build_parameters()
        DBSession.add(params)
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
       
        
       
         
      
        
        
        file_path = os.path.abspath(file.name)
        print 'Processing input %s' % file_path
        out_dir = track_directory()
        print 'to %s : ' % out_dir
        
        
        format = determine_format(file_path)
        print 'gessing format : %s' % format
        
        datatype = _formats.get(format, constants.NOT_DETERMINED_DATATYPE)
        datatype = constants.RELATIONAL
        
        print 'gessing datatype %s' % datatype
       
        
        dispatch = _process_dispatch.get(format,lambda *args, **kw : not_recognized(*args, **kw))
      
        print 'dispatch %s' % dispatch
        if trackname is None:
            trackname = file.name
            
        async_result = dispatch(datatype=datatype, path=file_path, sha1=sha1, name=trackname)
        print 'get async_result : %s' % async_result

        print 'building input'
        input = Input()
        input.sha1 = sha1
        input.datatype = datatype
       
        input.task_id = async_result.task_id
        
        DBSession.add(input)
        print 'deleting temporary file'
        try:
            os.remove(os.path.abspath(file.name))
        except OSError :
            pass
    DBSession.flush()
    return input   











'''
dicts that behave like a ``switch`` statement.
_process_dispatch : will choose where the inputed file should go at first.
_formats : to each format is associated a datatype.
_sql_dispatch : will choose in which process the database will go, based on it's datatype 

'''
_process_dispatch = {'sql' : lambda *args, **kw : move_database(*args, **kw),
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

_sql_dispatch = {'quantitative' : lambda *args, **kw : _signal(*args, **kw),
                 constants.SIGNAL : lambda *args, **kw : _signal(*args, **kw),
                 
                 'qualitative' :  lambda *args, **kw : _features(*args, **kw),
                 constants.FEATURES :  lambda *args, **kw : _features(*args, **kw),
                 
                 'extended' :  lambda *args, **kw : _relational(*args, **kw),
                  constants.RELATIONAL :  lambda *args, **kw : _relational(*args, **kw)
                 }




def move_database(datatype, path, sha1, name):
    '''
    Move the database to the right directory.
    Then process the database.
    '''
    out_name = '%s.%s' % (sha1, 'sql')
    print track_directory()
    dst = os.path.join(track_directory(), out_name)
    shutil.move(path, dst)
    return process_database(datatype, dst, sha1, name)


def process_database(datatype, path, sha1, name):
    '''
    Process the input as a SQLite database already build by the ``track`` package.
    @param datatype : the ``datatype`` of the file.
    @param path : the path of the database
    @param sha1 : the sha1 of the file
    @param name : the name of the track
    @return the task associated
    '''
    
    
    return _sql_dispatch.get(datatype, lambda *args, **kw : not_recognized(*args, **kw))(path, sha1, name)






def _signal(path, sha1, name):
    '''
    Process a ``signal`` database.
    @return the task associated
    '''
    return tasks.process_signal(path, sha1, name)

def _features(path, sha1, name):
    '''
    Process a ``feature`` database.
    @return the task associated
    '''
    return tasks.process_features(path, sha1, name, False)

def _relational(path, sha1, name):
    '''
    Process a ``relational`` database
    @return the task associated
    '''
    return tasks.process_features(path, sha1, name, True)
    


def not_recognized(datatype=None, **kw):
    '''
    Format not recognized
    '''
    pass

def not_impl():
    raise NotImplementedError

