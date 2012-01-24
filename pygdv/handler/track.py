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



def copy_track(user_id, track):
    to_copy = Track()
    to_copy.name = track.name
    to_copy.sequence_id = track.sequence_id
    to_copy.user_id = user_id
    to_copy.input_id = track.input_id
    DBSession.add(to_copy)
    DBSession.flush()
    params = TrackParameters()
    params.track = to_copy        
    params.build_parameters()
    DBSession.add(params)
    DBSession.add(to_copy)
    DBSession.flush()
    return to_copy

def delete(track_id, session=None):
    '''
    Delete the track and the input associated if this is the only track with this input.
    '''
    if session is None:
        session = DBSession
    track = session.query(Track).filter(Track.id == track_id).first()
    if track is not None:
        _input = track.input
        if len(_input.tracks) == 1:
            tasks.del_input.delay(_input.sha1)
            session.delete(_input)
        session.delete(track)
        session.flush()

def create_track(user_id, sequence, trackname=None, f=None, project=None, session=None, admin=False, force=False):
    if session is None:
        session = DBSession
    '''
    Create track from files :
    
        create input 
        create track from input
    
    @param trackname : name to give to the track
    @param file : the file name
    @param project : if given, the track created has to be added to the project 
    @return : task_id, track_id    
    '''
    if f is not None:
        _input = create_input(f,trackname, sequence.name, session, force=force)
        print 'create track : %s ' % _input
        if _input == constants.NOT_SUPPORTED_DATATYPE or _input == constants.NOT_DETERMINED_DATATYPE:
            try:
                os.remove(os.path.abspath(f))
            except OSError :
                pass
            return _input, 0

        track = Track()
        if trackname is not None:
            track.name = trackname
        track.sequence_id = sequence.id
        if not admin:
            track.user_id = user_id
        track.input_id = _input.id
        session.add(track)
        session.flush()
        
        
        params = TrackParameters()
        params.track = track        
        
        params.build_parameters()
        session.add(params)
        session.add(track)
        if project is not None:
            project.tracks.append(track)
            session.add(project)
            
        if admin :
            sequence.default_tracks.append(track)    
            session.add(sequence)
       
        session.flush()
        return _input.task_id, track.id
    
    
    
    

def create_input(f, trackname, sequence_name, session, force=False):
    '''
    Create an input if it's new, or simply return the id of an already inputed file 
    @param file : the file name
    @return : an Input
    '''
    sha1 = util.get_file_sha1(os.path.abspath(f))
    _input = session.query(Input).filter(Input.sha1 == sha1).first()
    if _input is not None and not force: 
        print "file already exist"
    else :
        if force :
            tasks.del_input(_input.sha1)
            
        file_path = os.path.abspath(f)
        out_dir = track_directory()
        
        
        fo = determine_format(file_path)

        dispatch = _process_dispatch.get(fo, constants.NOT_SUPPORTED_DATATYPE)
        if  dispatch == constants.NOT_SUPPORTED_DATATYPE:
            return dispatch
        
        
        datatype = _formats.get(fo, constants.NOT_SUPPORTED_DATATYPE)
        
        if datatype == constants.NOT_SUPPORTED_DATATYPE:
            return datatype
        
        elif datatype == constants.NOT_DETERMINED_DATATYPE:
            with track.load(file_path) as t:
                if t.datatype is not None:
                    datatype = _datatypes.get(t.datatype, constants.NOT_DETERMINED_DATATYPE)
        
        
        if datatype == constants.NOT_DETERMINED_DATATYPE:
            return datatype     

        if trackname is None:
            trackname = f
            
        
        async_result = dispatch(datatype=datatype, assembly_name=sequence_name, path=file_path,
                                sha1=sha1, name=trackname, tmp_file=f, format=fo)
        
        _input = Input()
        _input.sha1 = sha1
        _input.datatype = datatype
        
        _input.task_id = async_result.task_id
        
        session.add(_input)
        
    
    session.flush()
    return _input   







'''
dicts that behave like a ``switch`` statement.
_process_dispatch : will choose where the inputed file should go at first.
_formats : to each format is associated a datatype.
_sql_dispatch : will choose in which process the database will go, based on it's datatype 

'''
_process_dispatch = {'sql' : lambda *args, **kw : move_database(*args, **kw),
                    'bed' : lambda *args, **kw : convert_file(*args, **kw),
                    'gff' : lambda *args, **kw : convert_file(*args, **kw),
                    'gtf' : lambda *args, **kw : convert_file(*args, **kw),
                    'bigWig' : lambda *args, **kw : not_impl(*args, **kw),
                    'wig' : lambda *args, **kw : convert_file(*args, **kw),
                    'bedgraph' : lambda *args, **kw : convert_file(*args, **kw)}


_formats = {'sql' : constants.NOT_DETERMINED_DATATYPE,
                    'bed' : constants.FEATURES,
                    'gff' : constants.RELATIONAL,
                    'gtf' : constants.RELATIONAL,
                    'bigWig' : constants.SIGNAL,
                    'wig' : constants.SIGNAL,
                    'bedgraph' : constants.SIGNAL
                    }

_datatypes = {      constants.FEATURES : constants.FEATURES,
                    'qualitative' : constants.FEATURES,
                    'QUALITATIVE' : constants.FEATURES,
                    constants.SIGNAL : constants.SIGNAL,
                    'quantitative' : constants.SIGNAL,
                    'QUANTITATIVE' : constants.SIGNAL,
                    constants.RELATIONAL : constants.RELATIONAL,
                    'qualitative_extended' : constants.RELATIONAL,
                    'QUALITATIVE_EXTENDED' : constants.RELATIONAL,
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

def move_database(datatype, assembly_name, path, sha1, name, tmp_file, format):
    '''
    Move the database to the right directory.
    Then process the database.
    '''
    out_name = '%s.%s' % (sha1, 'sql')
    dst = os.path.join(track_directory(), out_name)
    shutil.move(path, dst)
    t = tasks.process_sqlite_file.delay(datatype, assembly_name, dst, sha1, name, format);
    return t

def convert_file(datatype, assembly_name, path, sha1, name, tmp_file, format):
    '''
    Convert a genomic file to a SQLite one using ``track`` package.
    '''
    out_name = '%s.%s' % (sha1, 'sql')
    dst = os.path.join(track_directory(), out_name)
    t = tasks.process_text_file.delay(datatype, assembly_name, path, sha1, name, format, out_name, dst)
    return t



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

