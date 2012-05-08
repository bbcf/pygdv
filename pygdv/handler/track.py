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
from tg.controllers import url


format_synonyms = {'db': 'sql',
                   'bw': 'bigwig',
                   'bwg': 'bigwig',
                   'wiggle_0': 'wig',}


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
            tasks.del_input(_input.sha1)
            session.delete(_input)
        session.delete(track)
        session.flush()

def create_track(user_id, sequence, f=None, trackname=None, project=None, session=None, admin=False, **kw):
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
        _input = create_input(f, trackname, sequence.name, session, force=kw.get('force', False), extension=kw.get('extension', None))
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
            project.user.tracks.append(track)
            session.add(project)
            
        if admin :
            sequence.default_tracks.append(track)    
            session.add(sequence)
       
        session.flush()
        return _input.task_id, track.id
    
    
    
    

def create_input(f, trackname, sequence_name, session, force=False, extension=None):
    '''
    Create an input if it's new, or simply return the id of an already inputed file 
    @param file : the file name
    @return : an Input
    '''
    sha1 = util.get_file_sha1(os.path.abspath(f))
    _input = session.query(Input).filter(Input.sha1 == sha1).first()
    if _input is not None and not force:
        try:
            os.remove(os.path.abspath(f));
        except OSError:
            pass
        print "file already exist"
    
    else :
        if _input is not None and force :
            tasks.del_input(_input.sha1)
            session.delete(_input)
            session.flush()

        file_path = os.path.abspath(f)
        out_dir = track_directory()
        
        if extension is not None:
            extension = extension.lower()
            fo = format_synonyms.get(extension, extension)
        else : 
            fo = determine_format(file_path)
            
            
        dispatch = _process_dispatch.get(fo, constants.NOT_SUPPORTED_DATATYPE)
        if  dispatch == constants.NOT_SUPPORTED_DATATYPE:
            return dispatch
        
        
        datatype = _formats.get(fo, constants.NOT_SUPPORTED_DATATYPE)
        
        if datatype == constants.NOT_SUPPORTED_DATATYPE:
            return datatype
        
        # format is sql => datatype can be signal or feature or extended
        elif datatype == constants.NOT_DETERMINED_DATATYPE:
            with track.load(file_path) as t:
                if t.datatype is not None:
                    datatype = _datatypes.get(t.datatype, constants.NOT_DETERMINED_DATATYPE)
        
        
        if datatype == constants.NOT_DETERMINED_DATATYPE:
            return datatype     

        if trackname is None:
            trackname = f
            
        
        async_result = dispatch(datatype=datatype, assembly_name=sequence_name, path=file_path,
                                sha1=sha1, name=trackname, tmp_file=f, _format=fo)
        
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


def move_database(datatype, assembly_name, path, sha1, name, tmp_file, _format):
    '''
    Move the database to the right directory.
    Then process the database.
    '''
    out_name = '%s.%s' % (sha1, 'sql')
    dst = os.path.join(track_directory(), out_name)
    shutil.move(path, dst)
    t = tasks.process_sqlite_file.delay(datatype, assembly_name, dst, sha1, name, _format)
    return t

def convert_file(datatype, assembly_name, path, sha1, name, tmp_file, _format):
    '''
    Convert a genomic file to a SQLite one using ``track`` package.
    '''
    out_name = '%s.%s' % (sha1, 'sql')
    dst = os.path.join(track_directory(), out_name)
    t = tasks.process_text_file.delay(datatype, assembly_name, path, sha1, name, _format, out_name, dst)
    return t


def link(track):
    return url('tracks/link?track_id=%s' % track.id)
