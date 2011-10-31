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



def create_track(user_id, sequence_id, trackname=None, f=None):
    '''
    Create track from files :
    
        create input 
        create track from input
    
    @param trackname : name to give to the track
    @param file : the file name
    '''
    print 'creating track'
    if f is not None:
        _input = create_input(f,trackname)
        if _input == constants.NOT_SUPPORTED_DATATYPE :
            print 'deleting temporary file'
            try:
                os.remove(os.path.abspath(f.name))
            except OSError :
                pass
            return constants.NOT_SUPPORTED_DATATYPE
        
        track = Track()
        if trackname is not None:
            track.name = trackname
        track.sequence_id = sequence_id
        track.user_id = user_id
        track.input_id = _input.id
        
        
        params = TrackParameters()
        DBSession.add(params)
        DBSession.flush()
        
        track.parameters = params
        
        
        DBSession.add(track)
        DBSession.flush()
        
        params.build_parameters()
        DBSession.add(params)
        DBSession.flush()
        return _input.task_id
    
    
    
    

def create_input(f, trackname):
    
    '''
    Create an input if it's new, or simply return the id of an already inputed file 
    @param file : the file name
    @return : an Input
    '''
    print 'creating input'
    sha1 = util.get_file_sha1(os.path.abspath(f))
    print "getting sha1 %s" % sha1
    _input = DBSession.query(Input).filter(Input.sha1 == sha1).first()
    if _input is not None: 
        print "file already exist"
    else :
        file_path = os.path.abspath(f)
        print 'Processing input %s' % file_path
        out_dir = track_directory()
        print 'to %s : ' % out_dir
        
        
        fo = determine_format(file_path)
        print 'gessing format : %s' % fo
        
        datatype = _formats.get(fo, constants.NOT_SUPPORTED_DATATYPE)
        print 'gessing datatype %s' % datatype
        
        if datatype == constants.NOT_SUPPORTED_DATATYPE:
            return datatype
        
        
        
       
       
        
        dispatch = _process_dispatch.get(fo, constants.NOT_SUPPORTED_DATATYPE)
        
        
        if  dispatch == constants.NOT_SUPPORTED_DATATYPE:
            return dispatch
      
        print 'dispatch %s' % dispatch
        if trackname is None:
            trackname = f
            
        datatype = constants.FEATURES
        
        async_result = dispatch(datatype=datatype, path=file_path, sha1=sha1, name=trackname)
        print 'get async_result : %s' % async_result

        print 'building input'
        _input = Input()
        _input.sha1 = sha1
        _input.datatype = datatype
       
        _input.task_id = async_result.task_id
        
        DBSession.add(_input)
    print 'deleting temporary file'
    try:
        os.remove(os.path.abspath(f))
    except OSError :
        pass
    DBSession.flush()
    return _input   








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
                    'bed' : constants.FEATURES,
                    'gff' : constants.RELATIONAL,
                    'bigWig' : constants.SIGNAL,
                    'wig' : constants.SIGNAL,
                    'bedgraph' : constants.SIGNAL
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

