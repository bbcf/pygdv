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
    execfile_path = os.path.abspath(os.path.join(constants.bin_directory_path, 'psd.jar'))
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
        'qualitative': constants.vizualisations['features'],
        'quantitative': constants.vizualisations['signal'],
        'extended': constants.vizualisations['relational'],
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
        out_directory = os.path.abspath(os.path.join(mappings['store'][fileinfo.extension], fileinfo.info['sha1']))

        fileinfo.paths['store'] = os.path.abspath(os.path.join(out_directory, '%s.sql' % fileinfo.trackname.split('.')[0]))
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
                async = mappings['process'][viz].delay(fileinfo, os.path.abspath(mappings['vizu_store'][viz]))
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
                async = mappings['process'][viz].delay(fileinfo, os.path.abspath(mappings['vizu_store'][viz]))
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
