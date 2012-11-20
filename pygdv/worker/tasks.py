from __future__ import absolute_import
from celery import task

import shutil, os, sys, traceback, json
from pygdv.lib.jbrowse import jsongen, scores
from pygdv.lib.constants import json_directory, track_directory, extra_directory
from celery.result import AsyncResult
from celery.signals import worker_init
from celery.task.http import HttpDispatchTask
from urllib2 import HTTPError
import time
from pygdv.lib import constants, util
import urllib, urllib2
from archive import Archive
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pygdv import model
from pygdv.lib import filemanager
from bbcflib import btrack
import hashlib

#convert("myfile.bed", "myfile.wig")


def init_model():
    import celery
    database_url = celery.current_app.conf['CELERY_RESULT_DBURI']

    maker = sessionmaker(autoflush=False, autocommit=False)
    DBSession = scoped_session(maker)
    DeclarativeBase = declarative_base()
    #metadata = DeclarativeBase.metadata

    DBSession.configure(bind=create_engine(database_url))
    return DBSession

DBSession = init_model()

mappings = {

}


class TR(object):
    """
    Dummy object for simple result propagation between chained tasks.
    More meaingful than using *args and indexes
    """
    def __init__(self):
        self.r = {}


@task()
def new_input(user_info, fileinfo, sequence_info):
    """
    Add an new input in GDV.
    fileinfo: a file info object.
    sequence_id: the sequence id
    """
    # upload | get sha1
    fileinfo = (upload.s(fileinfo) | sha1.s())().get()
    s = fileinfo.info['sha1']

    # TODO find fileinfo store
    # TODO set to sql to true or false

    # get the input
    inp = DBSession.query(model.Input).filter(model.Input.sha1 == s).first()

    # get the sequence
    seq = DBSession.query(model.Sequence).filter(model.Sequence.id == sequence_id).first()

    if inp is None:
        inp = model.Input()
        inp.sha1 = s
        inp.path = fileinfo.paths['store']
        inp.task_id = new_input.request.id
        DBSession.add(inp)
        DBSession.flush()

        if fileinfo.tosql:
            # transform to sql
            fileinfo = (tosql.s(fileinfo, sequence_info['name']))().get()
        else:
            # move to store |
            fileinfo = (tostore.s(fileinfo))().get()

    # delete tmp directory
    fileinfo = deltmp.s(fileinfo).get()

    fileinfo.info['input_id'] = inp.id

    # Track constructions
    # TODO mapping vizu
    # TODO launche processes => may contruct more than one track
    track = model.Track()
    track.name = fileinfo.trackname
    track.input_id = inp.id
    track.user_id = user_info['id']
    track.sequence_id = sequence_info['id']
    #parameters = Column(JSONEncodedDict, nullable=True)
    #visualization = Column(VARCHAR(255), default='not determined')
    #path = Column(Unicode(), nullable=True)    depend on vizu

    #task_id = Column(VARCHAR(255), ForeignKey('Input.id', ondelete="CASCADE"), nullable=True)
    return finfo


@task()
def upload(fileinfo):
    """
    Upload a file.
    """
    if not fileinfo.states['uploaded']:
        fileinfo.download()
    return fileinfo


@task()
def sha1(fileinfo):
    """
    Compute the hex sha1 of a file.
    """
    if not 'sha1' in fileinfo.info:
        s = hashlib.sha1()
        with open(fileinfo.paths['upload_to'], 'rb') as infile:
            for chunk in iter(lambda: infile.read(128 * 64), ''):
                s.update(chunk)
        fileinfo.info['sha1'] = s.hexdigest()
    return fileinfo


@task()
def tosql(fileinfo, seq_name):
    """
    Transform a input file to an sql one.
    """
    btrack.convert(fileinfo.paths['upload_to'], fileinfo.paths['store'], chrmeta=seq_name)


@task()
def deltmp(fileinfo):
    """
    Delete the original uploaded file.
    """
    if not fileinfo.states['tmpdel']:
        shutil.rmtree(os.path.split(fileinfo.paths['upload_to'][0]))
        fileinfo.states['tmpdel'] = True
    return fileinfo


@task()
def tostore(fileinfo):
    """
    Move a file to it's storage location.
    """
    if not fileinfo.states['instore']:
        shutil.move(fileinfo.paths['upload_to'], fileinfo.paths['store'])
        fileinfo.states['instore'] = True
    return fileinfo


@task()
def multiple_track_input(_uploaded, _file, _url, _fsys, sequence_id, user_mail, user_key, project_id, force, delfile, _callback_url, _extension):
    tmp_dir = tempfile.mkdtemp(dir=temporary_directory)
    if _uploaded:
        Archive(_file).extract(out=tmp_dir)
        os.remove(_file)
    else:
        for ul in _url.split():
            ul = util.norm_url(ul)
            fname = util.url_filename(ul)
            try:
                u = urllib2.urlopen(ul)
                block_sz = 2048
                outf = os.path.join(tmp_dir, fname)
                with open(outf, 'w') as tmp_file:
                        while True:
                            buffer = u.read(block_sz)
                            if not buffer:
                                break
                            tmp_file.write(buffer)
            except HTTPError as e:
                print '%s: %s' % (ul, e)
                raise e
            if util.is_compressed(os.path.splitext(fname)[1]):
                Archive(outf).extract(out=tmp_dir)
                os.remove(outf)


    outs = []
    for dir, dirs, files in os.walk(tmp_dir):
        outs.extend([os.path.abspath(os.path.join(dir, f)) for f in files])
    print "outs    %s " % ", ".join(outs)
    for _f in outs:
        callback(_callback_url + '/create', {'fsys':_f,
                                             'sequence_id': sequence_id,
                                             'mail': user_mail,
                                             'key': user_key,
                                             'project_id': project_id,
                                             'force': force,
                                             'delfile': True,
                                             'extension': os.path.splitext(_f)[1]
        })


@task()
def track_input(_uploaded, _file, _urls, _fsys, _track_name, _extension, _callback_url, _force, _track_id, _user_mail, _user_key, _sequence_id, delfile):
    """
    First Entry point for track processing:
    1) the track is uploaded (if it's not already the case)
    2) the sha1 of the track is calculated.
    3) callback at any time if the process fail, or at the end with success
    """

    task_id = track_input.request.id
    _fname = upload(_uploaded, _file, _urls, _fsys, _track_name, _extension, delfile)
    sha1 = util.get_file_sha1(_fname)
    result = callback(_callback_url + '/after_sha1', {'fname': _fname,
                                                 'sha1': sha1,
                                                 'force': _force,
                                                 'callback_url': _callback_url,
                                                 'track_id': _track_id,
                                                 'mail': _user_mail,
                                                 'key': _user_key,
                                                 'old_task_id': task_id,
                                                 'sequence_id': _sequence_id,
                                                 'extension': _extension,
                                                 'trackname': _track_name
                                                  })
    if result.has_key('error'):
        raise Exception(result.get('error'))


@task()
def track_process(_usermail, _userkey, old_task_id, fname, sha1, callback_url, track_id, sequence_name, extension, trackname, _callback_url):
    """
    Second entry point for track processing:
     4) the track is converted to sqlite format (if it's not already the case)
     5) the sqlite track is computed with two differents process for
         signal track: with an external jar file (psd.jar)
         features track: with jbrowse internal library
     6) callback at any time if the process fail, or at the end with success
     """
    from pygdv import handler

    out_name = '%s.%s' % (sha1, 'sql')
    dst = os.path.join(track_directory(), out_name)

    datatype = constants.NOT_DETERMINED_DATATYPE

    # move sqlite file
    if handler.track.is_sqlite_file(fname):
        datatype = btrack.track(fname, format='sql', readonly=True).info.get('datatype')
        shutil.move(fname, dst)
        if datatype is None:
            raise Exception("The datatype of your SQLite file is not defined: set it to 'signal' or 'features'.")
    # process text file
    else:
        try:
            btrack.convert(extension and (fname, extension) or fname, dst)
            datatype = handler.track.guess_datatype(extension)
            with btrack.track(dst, format='sql', info={'datatype': datatype},
                              assembly=sequence_name) as t:
                t.save()
            try:
                os.remove(os.path.abspath(fname))
            except OSError:
                pass
        except Exception as e:
            etype, value, tb = sys.exc_info()
            traceback.print_exception(etype, value, tb)
            callback(_callback_url + '/after_process', {'old_task_id': old_task_id,
                                                        'mail': _usermail,
                                                        'key': _userkey,
                                                        'track_id': 'None',
                                                        'datatype': datatype
            })
            raise e

    # process sqlite file
    if datatype == constants.NOT_DETERMINED_DATATYPE:
        raise Exception("Extension %s is not supported." % extension)

    try:
        dispatch = _sqlite_dispatch.get(datatype.lower())
        dispatch(dst, sha1, trackname)
    except Exception as e:
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
        os.remove(dst)
        result = callback(_callback_url + '/after_process', {'old_task_id': old_task_id,
                                                             'mail': _usermail,
                                                             'key': _userkey,
                                                             'track_id': 'None',
                                                             'datatype': datatype
        })
        raise e

    result = callback(_callback_url + '/after_process', {'old_task_id': old_task_id,
                                                         'mail': _usermail,
                                                         'key': _userkey,
                                                         'track_id': track_id,
                                                         'datatype': datatype
    })









def upload(_uploaded, _file, _urls, _fsys, _track_name, _extension, delfile):
    """
    Upload the track.
    """
    # file already uploaded
    if _uploaded:
        return _file
    
    _f = util.download(url=_urls,
                        fsys=_fsys,
                       filename=_track_name,
                       extension=_extension)

    # remove original file
    if _fsys is not None:
        if (isinstance(delfile, bool) and delfile) or (isinstance(delfile, basestring) and delfile.lower() in ['1', 'true', 'yes']):
            try:
                os.remove(_fsys)
            except OSError:
                pass
    return _f.name
        


def callback(url, parameters):
    print 'callback to %s with %s' % (url, parameters)
    req = urllib2.urlopen(url, urllib.urlencode(parameters))
    return json.loads(req.read())



import subprocess





_sqlite_dispatch = {'quantitative': lambda *args, **kw: _signal_database(*args, **kw),
                 constants.SIGNAL: lambda *args, **kw: _signal_database(*args, **kw),

                 'qualitative':  lambda *args, **kw: _features_database(*args, **kw),
                 constants.FEATURES:  lambda *args, **kw: _features_database(*args, **kw),

                 'extended':  lambda *args, **kw: _relational_database(*args, **kw),
                  constants.RELATIONAL:  lambda *args, **kw: _relational_database(*args, **kw)
                  }



def _signal_database(path, sha1, name):
    '''
    Process a``signal`` database.
    @return the subtask associated
    '''
    output_dir = json_directory()
    bin_dir = constants.bin_directory()
    path = os.path.abspath(path)
    print '[x] starting task ``compute scores``: db (%s), sha1(%s)' % (path, sha1)
    script = 'psd.jar'
    efile = os.path.join(bin_dir, script)
    p = subprocess.Popen(['java', '-jar', efile, path, sha1, output_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = p.wait()
    if result == 1:
        err = ', '.join(p.stderr)
        raise Exception(err)
    jsongen.jsonify_quantitative(sha1, output_dir, path)

def _features_database(path, sha1, name):
    '''
    Launch the process to produce a JSON output for a ``feature`` database.
    '''
    print 'json gen  db (%s), sha1(%s)' % (path, sha1)
    output_dir = json_directory()
    jsongen.jsonify(path, name, sha1, output_dir, '/data/jbrowse', '', False)


def _relational_database(path, sha1, name):
    '''
    Task for a ``relational`` database
    @return the subtask associated
    '''
    print 'json gen  db (%s), sha1(%s)' % (path, sha1)
    output_dir = json_directory()
    jsongen.jsonify(path, name, sha1, output_dir, '/data/jbrowse', '', True)





