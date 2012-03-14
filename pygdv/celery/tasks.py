from __future__ import absolute_import
from celery.task import task, chord, subtask
from celery.task.sets import TaskSet
import shutil, os, sys, traceback, json
from pygdv.lib.jbrowse import jsongen, scores
from pygdv.lib.constants import json_directory, track_directory
from celery.result import AsyncResult
from celery.signals import worker_init

from pygdv.lib import constants, util
import track, transaction
from pygdv.celery import model
from sqlalchemy.sql.expression import except_
from pygdv.model.database import TMPTrack
from bbcflib.genrep import GenRep

success = 1


manager = None

def session_connection(*args, **kw):
    print 'init of sessions args : %s, kw : %s' %(args, kw)
    import pygdv.celery.model
    
    
worker_init.connect(session_connection)




import subprocess





@task()
def plugin_process(plugin_id, _private_params, *args, **kw):
    from pygdv.handler.plugin import get_plugin_byId
    plug = get_plugin_byId(plugin_id, model.Manager)
    if plug :
        _private_params = json.loads(_private_params)
        session = model.DBSession()
        _private_params['session'] = session 
        _private_params['project'] = session.query(model.Project).filter(model.Project.id == _private_params['project_id']).first()
        kw.update(_private_params)
        value = plug.plugin_object.process(*args, **kw)
        session.commit()
        session.close()
        return value
    return 0


@task()
def test(x):
    print 'this is a test %s' % x
    return x



import datetime

@task()
def erase_data_from_public_user(delta=datetime.timedelta(days = 14)):
    print 'erase data from public user older than %s' % delta
    session = model.DBSession()
    try :
        public_user = session.query(model.User).filter(model.User.email == constants.public_user_email).first()
        for t in public_user.tracks:
            now = datetime.datetime.now()
            if delta < (now - t._created):
                from pygdv.handler.track import delete
                delete(t.id, session)
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.flush()
        session.close()








#############################################################################################################
#        FILE PROCESSING
#############################################################################################################
@task(max_retries=1)
def del_input(sha1, *args, **kw):
    '''
    Verify if the file are well processed.
    If no, it will erase the directory created in the
    tracks directory
    @param tasks : a list of return result. If one is different from 1, the directory is erased.
    '''
    path1 = os.path.join(track_directory(), sha1 + '.sql')
    path2 = os.path.join(json_directory(), sha1)
    try :
        os.remove(path1)
    except OSError: 
        pass
    shutil.rmtree(path2, ignore_errors = True)
    return 1


@task(max_retries=1)
def del_file_on_error(tasks, sha1, *args, **kw):
    '''
    Verify if the file are well processed.
    If no, it will erase the directory created in the
    tracks directory
    @param tasks : a list of return result. If one is different from 1, the directory is erased.
    '''
    print 'del file on error tasks :%s, sha1 : %s in %s and %s' % (tasks, sha1, track_directory(), json_directory())
    for theid in tasks:
        if not theid == success :
            path1 = os.path.join(track_directory(), sha1 + '.sql')
            path2 = os.path.join(json_directory(), sha1)
            try :
                os.remove(path1)
            except OSError: 
                pass
            shutil.rmtree(path2, ignore_errors = True)
            raise theid
    return 1


@task()
def convert(path, dst, sha1, datatype, assembly_name, name, tmp_file, _format, process_db=None, callback_on_error=None):

    print 'converting %s to %s using the assembly %s' %(path, dst, assembly_name)
    track.convert(_format and (path, _format) or path, dst)
    with track.load(dst, 'sql', readonly=False) as t:
        t.datatype = datatype
        t.assembly = assembly_name
    
    try:
        os.remove(os.path.abspath(path))
    except OSError :
        pass






#### GFEATMINER ####
import gMiner

@task()
def gfeatminer_request(user_id, project_id, req, job_description, job_name):
    '''
    Launch a gFeatMiner request.
    '''
    print 'gfeatminer request %s : ' % req
    session = model.DBSession()
    try :
        data = gMiner.run(**req)
        print 'gMiner ended with %s ' % data
        for path in data:
            if os.path.splitext(path)[1] == '.sql':
               
                project = session.query(model.Project).filter(model.Project.id == project_id).first()
                from pygdv.handler.track import create_track
                task_id, track_id = create_track(user_id, project.sequence, f=path, trackname='%s %s' 
                                             % (job_name, job_description), project=project, session = session)
    except Exception as e:
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
        session.rollback()
        raise e
   
    finally:
        session.commit()
        session.close()
       







### TRACK PROCESSING ###




@task()
def process_track(user_id, **kw):
    '''
    Entry point for uploading and processing tracks.
    '''
    session = model.DBSession()
    if not GenRep().is_up():
        if 'tmp_track_id' in kw:
            
            tmp_track = session.query(TMPTrack).filter(TMPTrack.id == kw['tmp_track_id']).first()
            tmp_track.status="FAILURE"
            tmp_track.traceback = 'GenRep service is down. Please Try again later'
            session.commit()
            session.close()
            raise Exception('GenRep service is down. Please Try again later')
        
    if not 'assembly' in kw and not 'project_id' in kw:
        raise Exception('Missing assembly parameters.')
    assembly_id = kw.get('assembly', None)
    files = None
    try :
        files = util.upload(**kw)
    except Exception as e:
        if 'tmp_track_id' in kw:
            session = model.DBSession()
            tmp_track = session.query(TMPTrack).filter(TMPTrack.id == kw['tmp_track_id']).first()
            tmp_track.status="FAILURE"
            tmp_track.traceback = 'Cannot download data.'
            session.commit()
            raise e
    finally:
        session.close()
        
        
    
        
    
    if files is None:
        if 'tmp_track_id' in kw:
            session = model.DBSession()
            tmp_track = session.query(TMPTrack).filter(TMPTrack.id == kw['tmp_track_id']).first()
            tmp_track.status="FAILURE"
            tmp_track.traceback = 'Cannot download data.'
            session.commit()
        raise Exception('No files to upload')
    
    
    project = None
    
    if 'tmp_track_id' in kw:
        tmp_track = session.query(TMPTrack).filter(TMPTrack.id == kw['tmp_track_id']).first()
        session.delete(tmp_track)
        session.flush()
    try :
        admin = False
        
        if 'admin' in kw:
            admin = kw['admin']
            
        if 'project_id' in kw:
            project = session.query(model.Project).filter(model.Project.id == kw['project_id']).first()
            if project is None:
                raise Exception('Project with id %s not found.' % kw['project_id'])
            assembly_id = project.sequence_id
    
        if not assembly_id:
            raise Exception('Missing assembly parameters.')
        
            
        for filename, f, extension in files:
            sequence = session.query(model.Sequence).filter(model.Sequence.id == assembly_id).first()
            if sequence is None:
                raise Exception('Sequence not found on GDV.')
            from pygdv.handler.track import create_track
            kw['extension'] = extension
            kw['admin'] = admin
            if 'trackname'in kw:
                del kw['trackname']
            task_id, track_id = create_track(user_id, sequence, f=f.name, trackname=filename, project=project, session=session, **kw)
            
            if task_id == constants.NOT_SUPPORTED_DATATYPE or task_id == constants.NOT_DETERMINED_DATATYPE:
                raise Exception('format %s' % task_id)
            
    except Exception as e:
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
        session.rollback()        
        raise e
    
    finally:
        session.commit()
        session.close()
    
    
    
@task()
def process_sqlite_file(datatype, assembly_name, path, sha1, name, format):
    '''
    Entry point of the sqlite file.
    '''
    try :
        dispatch = _sqlite_dispatch.get(datatype)
        dispatch(path, sha1, name)
    except Exception as e:
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
        del_input(sha1)
        raise e

@task()
def process_text_file(datatype, assembly_name, path, sha1, name, _format, tmp_file, destination):
    '''
    Entry point of the text file.
    '''
    try :
        convert(path, destination, sha1, datatype, assembly_name, name, tmp_file, _format)
        try:
            os.remove(path)
        except OSError:
            pass
        dispatch = _sqlite_dispatch.get(datatype)
        dispatch(destination, sha1, name)
    except Exception as e:
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
        del_input(sha1)
        raise e




### DATABASE PROCESSING ###



_sqlite_dispatch = {'quantitative' : lambda *args, **kw : _signal_database(*args, **kw),
                 constants.SIGNAL : lambda *args, **kw : _signal_database(*args, **kw),

                 'qualitative' :  lambda *args, **kw : _features_database(*args, **kw),
                 constants.FEATURES :  lambda *args, **kw : _features_database(*args, **kw),

                 'extended' :  lambda *args, **kw : _relational_database(*args, **kw),
                  constants.RELATIONAL :  lambda *args, **kw : _relational_database(*args, **kw)
                  }



def _signal_database(path, sha1, name):
    '''
    Process a``signal`` database.
    @return the subtask associated
    '''
    output_dir = json_directory()
    bin_dir = constants.bin_directory()
    print '[t] starting task ``compute scores`` : db (%s), sha1(%s)' % (path, sha1)
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




 
