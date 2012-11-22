from __future__ import absolute_import
from celery import task
import track
import shutil
import os
from pygdv.lib.jbrowse import jsongen
from pygdv.lib import constants
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from pygdv import model
from bbcflib import btrack
import hashlib
import subprocess

#convert("myfile.bed", "myfile.wig")


DEBUG_LEVEL = 1


def debug(s, t=0):
    if DEBUG_LEVEL > 0:
        print '[celery] %s%s' % ('\t' * t, s)


def init_model():
    import celery
    database_url = celery.current_app.conf['CELERY_RESULT_DBURI']

    maker = sessionmaker(autoflush=False, autocommit=True)
    DBSession = scoped_session(maker)
    #DeclarativeBase = declarative_base()
    #metadata = DeclarativeBase.metadata

    DBSession.configure(bind=create_engine(database_url))
    return DBSession

DBSession = init_model()


@task()
def signal(fileinfo, output_directory):
    debug('Signal %s' % fileinfo)
    execfile_path = os.path.join(constants.bin_directory_path, 'psd.jar')
    input_file_path = fileinfo.paths['store']
    debug('execfile_path : %s, input_file_path: %s, output_directory: %s' % (execfile_path, input_file_path, output_directory), 1)
    p = subprocess.Popen(['java', '-jar', execfile_path, input_file_path, fileinfo.info['sha1'], output_directory], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = p.wait()
    if result == 1:
        err = ', '.join(p.stderr)
        raise Exception(err)
    debug('Jsonify signal', 1)
    jsongen.jsonify_quantitative(fileinfo.info['sha1'], output_directory, input_file_path)


@task()
def features(fileinfo, output_directory):
    debug('Features %s' % fileinfo)
    input_file_path = fileinfo.paths['store']
    jsongen.jsonify(input_file_path, fileinfo.trackname, fileinfo.info['sha1'], output_directory, '/data/jbrowse/features', 'features', False)


@task()
def relational(fileinfo, output_directory):
    debug('Relational %s' % fileinfo)
    input_file_path = fileinfo.paths['store']
    jsongen.jsonify(input_file_path, fileinfo.trackname, fileinfo.info['sha1'], output_directory, '/data/jbrowse/relational', 'relational', True)


extensions = ['sql', 'bed', 'gff', 'gtf', 'bigwig', 'bw', 'wig', 'wiggle', 'bedgraph', 'bam', 'sam']

mappings = {
    'store': {
        'sql': constants.storage['data']['sql'],
        'bed': constants.storage['data']['sql'],
        'gff': constants.storage['data']['sql'],
        'gtf': constants.storage['data']['sql'],
        'bigwig': constants.storage['data']['sql'],
        'bw': constants.storage['data']['sql'],
        'wig': constants.storage['data']['sql'],
        'wiggle': constants.storage['data']['sql'],
        'bedgraph': constants.storage['data']['sql'],
        'bam': constants.storage['data']['bam'],
        'sam': constants.storage['data']['bam']
    },
    'vizu_store': {
        'signal': constants.storage['vizu']['signal'],
        'relational': constants.storage['vizu']['relational'],
        'features': constants.storage['vizu']['features']
    },
    'tosql': {
        'sql': False,
        'bed': True,
        'gff': True,
        'gtf': True,
        'bigwig': True,
        'bw': True,
        'wig': True,
        'wiggle': True,
        'bedgraph': True,
        'bam': False,
        'sam': False
    },
    'viz': {
        'bed': constants.vizualisations['features'],
        'gff': constants.vizualisations['relational'],
        'gtf': constants.vizualisations['relational'],
        'bigwig': constants.vizualisations['signal'],
        'bw': constants.vizualisations['signal'],
        'wig': constants.vizualisations['signal'],
        'wiggle': constants.vizualisations['signal'],
        'bedgraph': constants.vizualisations['signal'],
        'bam': constants.vizualisations['bam'],
        'sam': constants.vizualisations['bam'],
        'signal': constants.vizualisations['signal'],
        'features': constants.vizualisations['features'],
        'relational': constants.vizualisations['relational'],
    },
    'process': {
        'signal': signal,
        'features': features,
        'relational': relational
    }

}


@task()
def new_input(user_info, fileinfo, sequence_info, track_id, project_id=None):
    """
    Add an new input in GDV.
    """
    debug('New input uinfo : %s, sequenceinfo :%s, fileinfo : %s' % (user_info, sequence_info, fileinfo))
    output_directory = None
    trackcreated = DBSession.query(model.Track).filter(model.Track.id == track_id).first()
    try:
        # upload | get sha1
        fileinfo = upload(fileinfo)
        fileinfo = sha1(fileinfo)
        s = fileinfo.info['sha1']
        # guess extension
        fileinfo = guess_extension(fileinfo)
        fileinfo.states['tosql'] = mappings['tosql'][fileinfo.extension]

        # where put the input file
        out_directory = os.path.join(mappings['store'][fileinfo.extension], fileinfo.info['sha1'])

        fileinfo.paths['store'] = os.path.join(out_directory, '%s.sql' % fileinfo.trackname.split('.')[0])
        try:
            # mk output dir
            os.mkdir(out_directory)
        except OSError:
            pass
        # which vizualizations to launch
        fileinfo = guess_vizualisations(fileinfo)

        # get the input
        inp = DBSession.query(model.Input).filter(model.Input.sha1 == s).first()

        if inp is None:
            inp = model.Input()
            inp.sha1 = s
            inp.path = fileinfo.paths['store']
            inp.task_id = new_input.request.id
            DBSession.add(inp)
            DBSession.flush()
            debug('New input %s' % inp.id, 2)
            if fileinfo.states['tosql']:
                # transform to sql
                fileinfo = tosql(fileinfo, sequence_info['name'])
            else:
                # move to store
                fileinfo = tostore(fileinfo)
    except:

        trackcreated.task_id = new_input.request.id
        DBSession.flush()
        raise
    finally:
        # (if input is already in the store, just delete the file)
        # delete tmp directory
        fileinfo = deltmp(fileinfo)
        if output_directory is not None:
            debug('deleting output dir %s' % out_directory, 3)
            shutil.rmtree(out_directory)

    fileinfo.info['input_id'] = inp.id

    project = None
    if project_id is not None:
        project = DBSession.query(model.Project).filter(model.Project.id == project_id).first()
    # launch vizualisation
    for index, viz in enumerate(fileinfo.vizualisations):
        debug(viz, 2)
        out_directory = os.path.join(mappings['vizu_store'][viz], fileinfo.info['sha1'])
        if index == 0:
            t = trackcreated
        else:
            t = model.Track()
        t.name = fileinfo.trackname
        t.input_id = inp.id
        t.user_id = user_info['id']
        t.sequence_id = sequence_info['id']
        t.visualization = viz
        t.output_directory = out_directory
        if not os.path.exists(out_directory):
            try:
                async = mappings['process'][viz].delay(fileinfo, mappings['vizu_store'][viz])
                t.task_id = async.task_id
            except:
                shutil.rmtree(out_directory, ignore_errors=True)
                raise
        else:
            # try to look if there is a track with this task_id
            # and if it's a SUCCESS, else delete the directory to relauch the job
            other_track = DBSession.query(model.Track).filter(model.Track.output_directory == out_directory).first()
            if other_track is not None and other_track.status == constants.SUCCESS:
                t.task_id = other_track.task_id
            else:
                # no track or other_track not SUCCESS
                shutil.rmtree(out_directory)
                async = mappings['process'][viz].delay(fileinfo, mappings['vizu_store'][viz])
                t.task_id = async.task_id
                if other_track is not None:
                    other_tracks = DBSession.query(model.Track).filter(model.Track.output_directory == out_directory).all()
                    for oth in other_tracks:
                        oth.task_id = async.task_id
        if project is not None:
            project.tracks.append(t)

        DBSession.add(t)

    DBSession.flush()
    #parameters = Column(JSONEncodedDict, nullable=True)
    #visualization = Column(VARCHAR(255), default='not determined')
    #path = Column(Unicode(), nullable=True)    depend on vizu

    #task_id = Column(VARCHAR(255), ForeignKey('Input.id', ondelete="CASCADE"), nullable=True)
    debug('End %s' % fileinfo, 1)
    return fileinfo


@task()
def guess_vizualisations(fileinfo):
    debug('guess vizualisation', 3)
    if not fileinfo.extension == 'sql':
        fileinfo.vizualisations.extend(mappings['viz'][fileinfo.extension])
        debug(', '.join(fileinfo.vizualisations), 4)
        return fileinfo
    dt = btrack.track(fileinfo.paths['upload_to']).info['datatype']
    if dt is not None and dt.lower() in mappings['viz']:
        fileinfo.vizualisations.extend(mappings['viz'][dt.lower()])
        debug(', '.join(fileinfo.vizualisations), 4)
        return fileinfo
    raise Exception('Cannot guess the vizualisation for fileinfo "%s".' % fileinfo)


@task()
def guess_extension(fileinfo):
    debug('guess extension', 3)
    if fileinfo.extension in extensions:
        debug(fileinfo.extension, 4)
        return fileinfo
    file_path = fileinfo.paths['upload_to']
    if fileinfo.states['instore']:
        file_path = fileinfo.paths['store']
    with open(file_path, 'r') as infile:
        if infile.read(15) == 'SQLite format 3':
            fileinfo.extension = 'sql'
            debug(fileinfo.extension, 4)
            return fileinfo
    raise Exception('Cannot guess the extension for fileinfo "%s".' % fileinfo)


@task()
def upload(fileinfo):
    """
    Upload a file.
    """
    if not fileinfo.states['uploaded']:
        debug('Upload', 2)
        try:
            fileinfo.download()
        except IOError:
            raise IOError('Cannot download file from %s' % fileinfo.paths['in'])
    debug('Uploaded at %s' % fileinfo.paths['upload_to'], 3)
    return fileinfo


@task()
def sha1(fileinfo):
    """
    Compute the hex sha1 of a file.
    """
    debug('Sha1', 3)
    if not 'sha1' in fileinfo.info:
        s = hashlib.sha1()
        with open(fileinfo.paths['upload_to'], 'rb') as infile:
            for chunk in iter(lambda: infile.read(128 * 64), ''):
                s.update(chunk)
        fileinfo.info['sha1'] = s.hexdigest()
    debug('%s' % fileinfo.info['sha1'], 4)
    return fileinfo


@task()
def tosql(fileinfo, seq_name):
    """
    Transform a input file to an sql one.
    """
    debug('Tosql', 3)
    track.convert(fileinfo.extension and (fileinfo.paths['upload_to'], fileinfo.extension) or fileinfo.paths['upload_to'], fileinfo.paths['store'])
    with track.load(fileinfo.paths['store'], 'sql', readonly=False) as t:
        t.assembly = seq_name

    # debug('tosql : btrack.convert("%s", "%s", chrmeta="%s")' % (fileinfo.paths['upload_to'], fileinfo.paths['store'], seq_name), 3)
    # btrack.convert(fileinfo.paths['upload_to'], fileinfo.paths['store'], chrmeta=seq_name)
    fileinfo.states['instore'] = True
    debug('done', 4)
    return fileinfo


@task()
def deltmp(fileinfo):
    """
    Delete the original uploaded file.
    """
    debug('del tmp', 3)
    if not fileinfo.states['tmpdel']:
        shutil.rmtree(os.path.split(fileinfo.paths['upload_to'])[0])
        fileinfo.states['tmpdel'] = True
    return fileinfo


@task()
def tostore(fileinfo):
    """
    Move a file to it's storage location.
    """
    debug('to store', 3)
    if not fileinfo.states['instore']:
        shutil.move(fileinfo.paths['upload_to'], fileinfo.paths['store'])
        fileinfo.states['instore'] = True
    return fileinfo



# @task()
# def multiple_track_input(_uploaded, _file, _url, _fsys, sequence_id, user_mail, user_key, project_id, force, delfile, _callback_url, _extension):
#     tmp_dir = tempfile.mkdtemp(dir=temporary_directory)
#     if _uploaded:
#         Archive(_file).extract(out=tmp_dir)
#         os.remove(_file)
#     else:
#         for ul in _url.split():
#             ul = util.norm_url(ul)
#             fname = util.url_filename(ul)
#             try:
#                 u = urllib2.urlopen(ul)
#                 block_sz = 2048
#                 outf = os.path.join(tmp_dir, fname)
#                 with open(outf, 'w') as tmp_file:
#                         while True:
#                             buffer = u.read(block_sz)
#                             if not buffer:
#                                 break
#                             tmp_file.write(buffer)
#             except HTTPError as e:
#                 print '%s: %s' % (ul, e)
#                 raise e
#             if util.is_compressed(os.path.splitext(fname)[1]):
#                 Archive(outf).extract(out=tmp_dir)
#                 os.remove(outf)


#     outs = []
#     for dir, dirs, files in os.walk(tmp_dir):
#         outs.extend([os.path.abspath(os.path.join(dir, f)) for f in files])
#     print "outs    %s " % ", ".join(outs)
#     for _f in outs:
#         callback(_callback_url + '/create', {'fsys':_f,
#                                              'sequence_id': sequence_id,
#                                              'mail': user_mail,
#                                              'key': user_key,
#                                              'project_id': project_id,
#                                              'force': force,
#                                              'delfile': True,
#                                              'extension': os.path.splitext(_f)[1]
#         })


# @task()
# def track_input(_uploaded, _file, _urls, _fsys, _track_name, _extension, _callback_url, _force, _track_id, _user_mail, _user_key, _sequence_id, delfile):
#     """
#     First Entry point for track processing:
#     1) the track is uploaded (if it's not already the case)
#     2) the sha1 of the track is calculated.
#     3) callback at any time if the process fail, or at the end with success
#     """

#     task_id = track_input.request.id
#     _fname = upload(_uploaded, _file, _urls, _fsys, _track_name, _extension, delfile)
#     sha1 = util.get_file_sha1(_fname)
#     result = callback(_callback_url + '/after_sha1', {'fname': _fname,
#                                                  'sha1': sha1,
#                                                  'force': _force,
#                                                  'callback_url': _callback_url,
#                                                  'track_id': _track_id,
#                                                  'mail': _user_mail,
#                                                  'key': _user_key,
#                                                  'old_task_id': task_id,
#                                                  'sequence_id': _sequence_id,
#                                                  'extension': _extension,
#                                                  'trackname': _track_name
#                                                   })
#     if result.has_key('error'):
#         raise Exception(result.get('error'))


# @task()
# def track_process(_usermail, _userkey, old_task_id, fname, sha1, callback_url, track_id, sequence_name, extension, trackname, _callback_url):
#     """
#     Second entry point for track processing:
#      4) the track is converted to sqlite format (if it's not already the case)
#      5) the sqlite track is computed with two differents process for
#          signal track: with an external jar file (psd.jar)
#          features track: with jbrowse internal library
#      6) callback at any time if the process fail, or at the end with success
#      """
#     from pygdv import handler

#     out_name = '%s.%s' % (sha1, 'sql')
#     dst = os.path.join(track_directory(), out_name)

#     datatype = constants.NOT_DETERMINED_DATATYPE

#     # move sqlite file
#     if handler.track.is_sqlite_file(fname):
#         with track.load(fname, 'sql', readonly=True) as t:
#             datatype = t.datatype
#         shutil.move(fname, dst)
#         if datatype is None:
#             raise Exception("The datatype of your SQLite file is not defined: set it to 'signal' or 'features'.")
#     # process text file
#     else:
#         try:
#             track.convert(extension and (fname, extension) or fname, dst)
#             datatype = handler.track.guess_datatype(extension)
#             with track.load(dst, 'sql', readonly=False) as t:
#                 t.datatype = datatype
#                 t.assembly = sequence_name
#             try:
#                 os.remove(os.path.abspath(fname))
#             except OSError:
#                 pass
#         except Exception as e:
#             etype, value, tb = sys.exc_info()
#             traceback.print_exception(etype, value, tb)
#             callback(_callback_url + '/after_process', {'old_task_id': old_task_id,
#                                                         'mail': _usermail,
#                                                         'key': _userkey,
#                                                         'track_id': 'None',
#                                                         'datatype': datatype
#             })
#             raise e

#     # process sqlite file
#     if datatype == constants.NOT_DETERMINED_DATATYPE:
#         raise Exception("Extension %s is not supported." % extension)

#     try:
#         dispatch = _sqlite_dispatch.get(datatype.lower())
#         dispatch(dst, sha1, trackname)
#     except Exception as e:
#         etype, value, tb = sys.exc_info()
#         traceback.print_exception(etype, value, tb)
#         os.remove(dst)
#         result = callback(_callback_url + '/after_process', {'old_task_id': old_task_id,
#                                                              'mail': _usermail,
#                                                              'key': _userkey,
#                                                              'track_id': 'None',
#                                                              'datatype': datatype
#         })
#         raise e

#     result = callback(_callback_url + '/after_process', {'old_task_id': old_task_id,
#                                                          'mail': _usermail,
#                                                          'key': _userkey,
#                                                          'track_id': track_id,
#                                                          'datatype': datatype
#     })









# def upload(_uploaded, _file, _urls, _fsys, _track_name, _extension, delfile):
#     """
#     Upload the track.
#     """
#     # file already uploaded
#     if _uploaded:
#         return _file
    
#     _f = util.download(url=_urls,
#                         fsys=_fsys,
#                        filename=_track_name,
#                        extension=_extension)

#     # remove original file
#     if _fsys is not None:
#         if (isinstance(delfile, bool) and delfile) or (isinstance(delfile, basestring) and delfile.lower() in ['1', 'true', 'yes']):
#             try:
#                 os.remove(_fsys)
#             except OSError:
#                 pass
#     return _f.name
        


# def callback(url, parameters):
#     print 'callback to %s with %s' % (url, parameters)
#     req = urllib2.urlopen(url, urllib.urlencode(parameters))
#     return json.loads(req.read())



# import subprocess





# _sqlite_dispatch = {'quantitative': lambda *args, **kw: _signal_database(*args, **kw),
#                  constants.SIGNAL: lambda *args, **kw: _signal_database(*args, **kw),

#                  'qualitative':  lambda *args, **kw: _features_database(*args, **kw),
#                  constants.FEATURES:  lambda *args, **kw: _features_database(*args, **kw),

#                  'extended':  lambda *args, **kw: _relational_database(*args, **kw),
#                   constants.RELATIONAL:  lambda *args, **kw: _relational_database(*args, **kw)
#                   }




# def _relational_database(path, sha1, name):
#     '''
#     Task for a ``relational`` database
#     @return the subtask associated
#     '''
#     print 'json gen  db (%s), sha1(%s)' % (path, sha1)
#     output_dir = json_directory()
#     jsongen.jsonify(path, name, sha1, output_dir, '/data/jbrowse', '', True)

# def _features_database(path, sha1, name):
#     '''
#     Launch the process to produce a JSON output for a ``feature`` database.
#     '''
#     print 'json gen  db (%s), sha1(%s)' % (path, sha1)
#     output_dir = json_directory()
#     jsongen.jsonify(path, name, sha1, output_dir, '/data/jbrowse', '', False)


# def _signal_database(path, sha1, name):
#     '''
#     Process a``signal`` database.
#     @return the subtask associated
#     '''
#     output_dir = json_directory()
#     bin_dir = constants.bin_directory()
#     path = os.path.abspath(path)
#     print '[x] starting task ``compute scores``: db (%s), sha1(%s)' % (path, sha1)
#     script = 'psd.jar'
#     efile = os.path.join(bin_dir, script)
#     p = subprocess.Popen(['java', '-jar', efile, path, sha1, output_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     result = p.wait()
#     if result == 1:
#         err = ', '.join(p.stderr)
#         raise Exception(err)
#     jsongen.jsonify_quantitative(sha1, output_dir, path)






