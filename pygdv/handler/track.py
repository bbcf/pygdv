from __future__ import absolute_import
'''
Tracks handler.
'''

from pygdv.model import DBSession, Input, Track, TrackParameters, Task, Sequence, Project
import os, shutil, tg
from pygdv.model import constants
from pygdv.lib import util
from pygdv.celery import tasks
from pygdv.lib.constants import track_directory
from track.util import determine_format
from pygdv.lib import constants
import track, urlparse
from celery.task import task, chord, subtask, TaskSet
from pygdv.lib.constants import json_directory, track_directory

_formats = {'bed' : constants.FEATURES,
            'gff' : constants.RELATIONAL,
            'gtf' : constants.RELATIONAL,
            'bigwig' : constants.SIGNAL,
            'bw' : constants.SIGNAL,
            'wig' : constants.SIGNAL,
            'wiggle' : constants.SIGNAL,
            'bedgraph' : constants.SIGNAL
}

def is_sqlite_file(_f):
    """
    Guess if the file is sqlite3 or not
    """
    with open(_f, 'r') as _file:
        if _file.read(15) == 'SQLite format 3' : return True
    return False

def guess_datatype(extension):
    if _formats.has_key(extension):
        return _formats.get(extension)
    raise Exception('Cannot guess the datatype for extension "%s"' % extension)




def pre_track_creation(url=None, file_upload=None, fsys=None, project_id=None, sequence_id=None):
    """
    Verify track parameters.
    """
    if (file_upload is None or file_upload == '' ) and (url is None or url == '')and (fsys is None or fsys == ''):
        raise Exception("Missing file to upload.")

    if url is not None and url != '':
        u = urlparse.urlparse(url)
        if not u.hostname:
            url = 'http://%s' % url
            u = urlparse.urlparse(url)
            if not u.hostname:
                raise Exception("Malformed url parameter.")

    if project_id is None and sequence_id is None:
        raise Exception('Missing assembly parameter.')

    if project_id is not None:
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        if project is None:
            raise Exception('Project with id %s not found.' % project_id)
    if sequence_id is None:
        sequence_id = project.sequence_id
    sequence = DBSession.query(Sequence).filter(Sequence.id == sequence_id).first()
    if sequence is None:
        raise Exception('Sequence not found on GDV. Ask an admin to upload it.')

def fetch_track_parameters(url=None, file_upload=None, fsys=None, trackname=None, extension=None, project_id=None, sequence_id=None):
    """
    Fetch track parameters from the request.
    Guess trackname and extension if they are not provided.
    """
    if url == '' : url = None
    if file_upload == '' : file_upload = None
    if fsys == '' : fsys = None
    tn = ext = None
    if trackname is None:
        if url is not None:
            url = util.norm_url(url)
            tn = util.url_filename(url)
            trackname = os.path.splitext(tn)[0]
        elif file_upload is not None:
            trackname = os.path.splitext(file_upload.filename)[0]
        elif fsys is not None:
            trackname = os.path.splitext(os.path.split(fsys)[1])[0]
    if extension is None:
        if url is not None:
            if tn is not None:
                extension =  os.path.splitext(tn)[1]
            else :
                extension = os.path.splitext(os.path.split(url)[1])[1]
        elif file_upload is not None:
            extension = os.path.splitext(file_upload.filename)[1]
        elif fsys is not None:
            extension = os.path.splitext(os.path.split(fsys)[1])[1]

    extension = extension.lower()

    # remove dot in the first position only
    if extension.find('.') == 0:
        extension = extension.replace('.','',1)

    if sequence_id is None:
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        sequence_id = project.sequence_id
        extension = extension.replace('.', '').lower()
    return trackname, extension, sequence_id

def new_track(user_id, track_name, sequence_id, admin=False, project_id=None):
    """
    Create a new track and Input in the database.
    :param user_id : the user identifier. Will not be set if the track is admin.
    :param admin: True if the track created is 'admin' ~ will be viewed by all users
    """
    # create input
    _input = Input()
    DBSession.add(_input)
    DBSession.flush()

    # create track
    _track = Track()
    _track.name = track_name
    _track.sequence_id = sequence_id
    _track.input_id = _input.id
    if not admin:
        _track.user_id = user_id

    if project_id is not None:
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        project.tracks.append(_track)
        DBSession.add(project)

    DBSession.add(_track)
    DBSession.flush()

    return _track

def finalize_track_creation(_track=None, track_id=None):
    if _track is None:
        _track = DBSession.query(Track).filter(Track.id == track_id).first()
    # track parameters
    params = TrackParameters()
    params.track = _track
    params.build_parameters()
    DBSession.add(params)
    DBSession.add(_track)


def update(track=None, track_id=None, params=None):
    """
    Update the track in the database
    :param track : the track
    :param track_id : the track_id to fetch the track if it's not provided
    :param params : a dict to tell what to update
    """
    if track is None:
        track = DBSession.query(Track).filter(Track.id == track_id).first()


    # set the task related with the track
    if params.has_key('task_id'):
        input = track.input
        if input is None:
            input = DBSession.query(Input).filter(Input.id == track.id).first()

        input.task_id = params.get('task_id')
        DBSession.add(input)
        
    # set the new task related with the track
    # the old one is deleted
    if params.has_key('new_task_id'):
        old_task_id = track.input.task_id
        track.input.task_id = params.get('new_task_id')
        DBSession.add(track)
    
    
    # set the input to the track. The old input belonging to the track 
    # is deleted
    if params.has_key('new_input_id'):
        old_input = track.input
        _input = DBSession.query(Input).filter(Input.id == int( params.get('new_input_id'))).first()
        _input.tracks.append(track)
        DBSession.add(_input)
        DBSession.delete(old_input)

    # set the sha1 for the track input
    if params.has_key('sha1'):
        input = track.input
        if input is None:
            input = DBSession.query(Input).filter(Input.id == track.id).first()
        input.sha1 = params.get('sha1')
        DBSession.add(input)

    if params.has_key('datatype'):
        track.input.datatype = params.get('datatype')
        DBSession.add(track)
    DBSession.flush()



def delete_input(sha1):
    '''
    Delete the input with the sha1 specified.
    Must delete in the "track directory" + '.sql' and
    in the "json directory"
    :param sha1 : the sha1 of the input
    '''
    if sha1 is not None:
        trackdir = os.path.join(track_directory(), sha1 + '.sql')
        try :
            os.remove(trackdir)
        except OSError:
            pass

        jsondir = os.path.join(json_directory(), sha1)
        shutil.rmtree(jsondir, ignore_errors = True)
















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

def delete_track(track=None, track_id=None):
    '''
    Delete the track and the input associated if this is the only track with this input.
    '''
    if track is None:
        track = DBSession.query(Track).filter(Track.id == track_id).first()
    if track is None: return
    _input = track.input
    if len(_input.tracks) == 1:
        delete_input(_input.sha1)
        DBSession.delete(_input)
    DBSession.delete(track)
    DBSession.flush()







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
            os.remove(os.path.abspath(f))
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
    return tg.config.get('main.proxy') + tg.url('/tracks/link?track_id=%s' % track.id)


def plugin_link(track):
    return tg.config.get('main.proxy') + tg.url('/') + track.rel_path


def edit(track=None, track_id=None, name=None, color=None):
    if track is None:
        track = DBSession.query(Track).filter(Track.id == track_id).first()
    if name is not None:
        track.name = name
    if color is not None:
        if track.parameters is None:
            params = TrackParameters()
            params.track = track
            params.color = color
            params.build_parameters()
            DBSession.add(params)
        else :
            track.parameters.color = color

    DBSession.add(track)
    DBSession.flush()

