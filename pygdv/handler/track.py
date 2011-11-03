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
import track
from celery.task import task, chord, subtask, TaskSet
from pygdv.lib.constants import json_directory, track_directory

def create_track(user_id, sequence, trackname=None, f=None):
    '''
    Create track from files :
    
        create input 
        create track from input
    
    @param trackname : name to give to the track
    @param file : the file name
    '''
    print 'creating track'
    if f is not None:
        _input = create_input(f,trackname, sequence.name)
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
        track.sequence_id = sequence.id
        track.user_id = user_id
        track.input_id = _input.id
        DBSession.add(track)
        DBSession.flush()
        
        params = TrackParameters()
        params.track = track        
        
        params.build_parameters()
        DBSession.add(params)
        DBSession.add(track)
        DBSession.flush()
        return _input.task_id
    
    
    
    

def create_input(f, trackname, sequence_name):
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
        
        dispatch = _process_dispatch.get(fo, constants.NOT_SUPPORTED_DATATYPE)
        if  dispatch == constants.NOT_SUPPORTED_DATATYPE:
            return dispatch
        
        
        datatype = _formats.get(fo, constants.NOT_SUPPORTED_DATATYPE)
        print 'gessing datatype %s' % datatype
        
        if datatype == constants.NOT_SUPPORTED_DATATYPE:
            return datatype
        
        elif datatype == constants.NOT_DETERMINED_DATATYPE:
            # this is an sql
            #make a track and guess datatype
            pass
       
      
        print 'dispatch %s' % dispatch
        if trackname is None:
            trackname = f
            
        
        async_result = dispatch(datatype=datatype, assembly_name=sequence_name, path=file_path,
                                sha1=sha1, name=trackname, tmp_file=f, format=fo)
        print 'get async_result : %s' % async_result

        print 'building input'
        _input = Input()
        _input.sha1 = sha1
        _input.datatype = datatype
       
        _input.task_id = async_result.task_id
        
        DBSession.add(_input)
        
    
    DBSession.flush()
    return _input   







'''
dicts that behave like a ``switch`` statement.
_process_dispatch : will choose where the inputed file should go at first.
_formats : to each format is associated a datatype.
_sql_dispatch : will choose in which process the database will go, based on it's datatype 

'''
_process_dispatch = {'sql' : lambda *args, **kw : move_database(*args, **kw),
                    'bed' : lambda *args, **kw : convert_file(*args, **kw),
                    'bigWig' : lambda *args, **kw : not_impl(*args, **kw),
                    'wig' : lambda *args, **kw : convert_file(*args, **kw),
                    'bedgraph' : lambda *args, **kw : convert_file(*args, **kw)}


_formats = {'sql' : constants.NOT_DETERMINED_DATATYPE,
                    'bed' : constants.FEATURES,
                    'gff' : constants.RELATIONAL,
                    'bigWig' : constants.SIGNAL,
                    'wig' : constants.SIGNAL,
                    'bedgraph' : constants.SIGNAL
                    }

#_sql_dispatch = {'quantitative' : lambda *args, **kw : _signal2(*args, **kw),
#                 constants.SIGNAL : lambda *args, **kw : _signal2(*args, **kw),
#                 
#                 'qualitative' :  lambda *args, **kw : _features2(*args, **kw),
#                 constants.FEATURES :  lambda *args, **kw : _features2(*args, **kw),
#                 
#                 'extended' :  lambda *args, **kw : _relational2(*args, **kw),
#                  constants.RELATIONAL :  lambda *args, **kw : _relational2(*args, **kw)
#                 }
#
#
#_sql_dispatch2 = {'quantitative' : lambda *args, **kw : _signal2(*args, **kw),
#                 constants.SIGNAL : lambda *args, **kw : _signal2(*args, **kw),
#                 
#                 'qualitative' :  lambda *args, **kw : _features2(*args, **kw),
#                 constants.FEATURES :  lambda *args, **kw : _features2(*args, **kw),
#                 
#                 'extended' :  lambda *args, **kw : _relational2(*args, **kw),
#                  constants.RELATIONAL :  lambda *args, **kw : _relational2(*args, **kw)
#                 }

def move_database(datatype, assembly_id, path, sha1, name, tmp_file, format):
    '''
    Move the database to the right directory.
    Then process the database.
    '''
    out_name = '%s.%s' % (sha1, 'sql')
    dst = os.path.join(track_directory(), out_name)
    shutil.move(path, dst)
    return tasks.process_database.delay(datatype, assembly_id, dst, sha1, name, format);

def convert_file(datatype, assembly_name, path, sha1, name, tmp_file, format):
    '''
    Convert a genomic file to a SQLite one using ``track`` package.
    '''
    out_name = '%s.%s' % (sha1, 'sql')
    dst = os.path.join(track_directory(), out_name)

    callback = subtask(task=tasks.del_file_on_error, args=(sha1,))
    t2 = subtask(tasks.process_database)
    t1 = tasks.convert.delay(path, dst, sha1, datatype, assembly_name, name, tmp_file, format, process_db=t2, callback_on_error=callback)
    return t1



#
#def process_database(datatype, path, sha1, name):
#    '''
#    Process the input as a SQLite database already build by the ``track`` package.
#    @param datatype : the ``datatype`` of the file.
#    @param path : the path of the database
#    @param sha1 : the sha1 of the file
#    @param name : the name of the track
#    @return the task associated
#    '''
#    
#    
#    return _sql_dispatch.get(datatype, lambda *args, **kw : not_recognized(*args, **kw))(path, sha1, name)





def _signal2(path, sha1, name):
    '''
    Task for a ``signal`` database.
    @return the subtask associated
    '''
    output_dir = json_directory()
    callback_on_error = subtask(task=tasks.del_file_on_error, args=(sha1,))
    t1 = tasks._compute_scores.delay(path, sha1, output_dir, callback=subtask(tasks._jsonify_signal, del_tmp=tasks.del_tmp_file), 
                                     callback_on_error=callback_on_error)
    return t1
    
    
    
    
    return tasks.process_signal(path, sha1, name)

def _features2(path, sha1, name):
    '''
    Task for a ``feature`` database.
    @return the subtask associated
    '''
    output_dir = json_directory()
    callback_on_error = subtask(task=tasks.del_file_on_error, args=(sha1,))
    
    t1 = tasks._jsonify_features.delay(path, name, sha1, output_dir, '/data/jbrowse', '', False,
                            callback_on_error=callback_on_error)
    return t1
    
    
    return tasks.process_features(path, sha1, name, False)

def _relational2(path, sha1, name):
    '''
    Task for a ``relational`` database
    @return the subtask associated
    '''
    output_dir = json_directory()
    callback_on_error = subtask(task=tasks.del_file_on_error, args=(sha1,))
    
    t1 = tasks._jsonify_features.delay(path, name, sha1, output_dir, '/data/jbrowse', '', True,
                            callback_on_error=callback_on_error)
    return t1


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

