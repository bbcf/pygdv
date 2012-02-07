from __future__ import absolute_import
from celery.task import task, chord, subtask
from celery.task.sets import TaskSet
import shutil, os, sys, traceback
from pygdv.lib.jbrowse import jsongen, scores
from pygdv.lib.constants import json_directory, track_directory
from celery.result import AsyncResult
from celery.signals import worker_init

from pygdv.lib import constants, util
import track
import tempfile, transaction
from pygdv.celery import model
from sqlalchemy.sql.expression import except_
success = 1




def session_connection(*args, **kw):
    print 'init of sessions args : %s, kw : %s' %(args, kw)
    import pygdv.celery.model
   
    
    
worker_init.connect(session_connection)





import subprocess
@task()
def test_command_line(*args, **kw):
    print 'start of task'
    p = subprocess.Popen('pwd')
    print p.__dict__
    bin_dir = constants.bin_directory()
    print bin_dir
    script = 'test.sh'
    e = os.path.join(bin_dir, script)
    p2 = subprocess.call(['sh', e])
    if p2 != 0:
        raise p2
    print 'end of task'
    return 1


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
def del_tmp_file(f):
    return 1
    print 'deleting temporary file'
    try:
        os.remove(os.path.abspath(f))
    except OSError :
        pass
    return 1




def process_features(database, sha1, name, extended = False):
    '''
    Process a ``features`` SQL file and create the databases needed by JBrowse.
    @param database : the database
    @param sha1 : the sah1 of the file
    @param name : the name of the output track
    @param extended : if the SQLite database is 'extended' format
    '''
    print '[t] starting task ``process features`` : db (%s), sha1(%s), name(%s), extended(%s).' % (database, sha1, name, extended)
    output_dir = json_directory()
    callback = subtask(task=del_file_on_error, args=(sha1, output_dir))

    return _jsonify_features.delay(database, name, sha1, output_dir, '/data/jbrowse', '', extended,
                            callback=callback)

#    job = chord(tasks = [
#            _jsonify_features.subtask((database, name, sha1, output_dir, '/data/jbrowse', '', extended))
#                   ])(callback)
#    return job





@task()
def _compute_scores(database, sha1, output_dir, callback=None, callback_on_error=None):
    '''
    Launch the process to pre-calculate scores on a signal database.
    '''
    print '[t] starting task ``compute scores`` : db (%s), sha1(%s)' % (database, sha1)
    try :
        
        bin_dir = constants.bin_directory()
        script = 'psd.jar'
        efile = os.path.join(bin_dir, script)
        p2 = subprocess.call(['java', '-jar', efile, database, sha1, output_dir])
        print p2
        print 'end of task'
        
        # old call
        #scores.pre_compute_sql_scores(database, sha1, output_dir)
        if callback :
            output_dir = json_directory()
            return subtask(callback).delay(sha1, output_dir, database, callback_on_error=callback_on_error)
    except Exception as e:
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
        if callback_on_error :
            subtask(callback_on_error).delay([e], sha1)
        raise e
    return 1


@task()
def _jsonify_signal(sha1, output_root_directory, database_path, callback_on_error=None, del_tmp=None):
    '''
    Launch the process to produce a JSON output for a ``signal`` database.
    '''
    print 'jsonify signal sha1 : %s, output dir : %s, path : %s ' % (sha1, output_root_directory, database_path)
    try :
        jsongen.jsonify_quantitative(sha1, output_root_directory, database_path)
    except Exception as e:
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
        if callback_on_error :
            subtask(callback_on_error).delay([e], sha1)
            raise e
    return 1


@task()
def _jsonify_features(database, name, sha1, output_dir, public_url, browser_url, extended, callback_on_error=None):
    '''
    Launch the process to produce a JSON output for a ``feature`` database.
    '''
    try :
        jsongen.jsonify(database, name, sha1, output_dir, public_url, browser_url, extended)
    except Exception as e:
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
        if callback_on_error :
            subtask(callback_on_error).delay([e], sha1)
            raise e
    return 1

simple_fields = ('start', 'end', 'score', 'name', 'strand')
ext_fields = ('start', 'end', 'score', 'name', 'strand', 'type', 'id')
agg_field = 'attributes'
signal_fields = ('start', 'end', 'score')

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


#@task()
#def convert2(path, dst, sha1, datatype, assembly_name, name, tmp_file, format, process_db=None, callback_on_error=None):
#
#    tfile = tempfile.NamedTemporaryFile(suffix='.sql', delete=True)
#    tmp_dst = tfile.name
#    tfile.close()
#    try:
#        
#        # normal convert
#        print 'converting %s to %s using the assembly %s' %(path, tmp_dst, assembly_name)
#        track.convert(path, tmp_dst)
#        # then tranform to GDV format
#        if datatype == constants.SIGNAL:
#            f = signal_fields
#            with track.load(tmp_dst, 'sql', readonly=True) as t:
#                with track.new(dst, 'sql') as t2:
#                    for chrom in t:
#                        
#                        t2.write(chrom, t.read(chrom, fields=signal_fields), fields=signal_fields)
#                    t2.datatype = constants.SIGNAL
#                    t2.assembly = assembly_name
#                    
#        elif datatype == constants.FEATURES:
#            f = simple_fields
#            with track.load(tmp_dst, 'sql', readonly=True) as t:
#                with track.new(dst, 'sql') as t2:
#                    for chrom in t:
#                        gen = t.aggregated_read(chrom, f)
#                        t2.write(chrom, gen, fields=f + (agg_field,))
#                    t2.datatype = constants.FEATURES
#                    t2.assembly = assembly_name
#
#
#        elif datatype == constants.RELATIONAL:
#            f = ext_fields
#            with track.load(tmp_dst, 'sql', readonly=True) as t:
#                with track.new(dst, 'sql') as t2:
#                    for chrom in t:
#                        gen = t.aggregated_read(chrom, f)
#                        t2.write(chrom, gen, fields=f + (agg_field,))
#                    t2.datatype = constants.RELATIONAL
#                    t2.assembly = assembly_name
#        
#        print 'removing tmp files'
#        try:
#            os.remove(os.path.abspath(path))
#        except OSError :
#            pass
#        try:
#            os.remove(os.path.abspath(tmp_dst))
#        except OSError :
#            pass
#
#        
#        if process_db :
#            return subtask(process_db).delay(datatype, assembly_name, dst, sha1, name, format)
#
#    except Exception as e:
#        etype, value, tb = sys.exc_info()
#        traceback.print_exception(etype, value, tb)
#        if callback_on_error :
#            subtask(callback_on_error).delay([e], sha1)
#            raise e
#    return 1


@task()
def process_database(datatype, assembly_name, path, sha1, name, format):
    pass
#
##### DATABASE PROCESS ####
#def check_database(path, sha1):
#    pass
#
#@task()
#def process_database(datatype, assembly_name, path, sha1, name, format):
#    '''
#    Entry point of the sqlite file.
#    '''
#    check_database(path, sha1)
#    dispatch = _sql_dispatch.get(datatype)
#    try :
#        t =  dispatch(path, sha1, name)
#        return t
#    except Exception as e:
#        etype, value, tb = sys.exc_info()
#        traceback.print_exception(etype, value, tb)
#        raise e
#



#    
#def cannot_process():
#    print '[x] ERROR [x] cannot process'
#    return -1;
#
#
#
#
#
#
#
#def _signal(path, sha1, name):
#    '''
#    Task for a ``signal`` database.
#    @return the subtask associated
#    '''
#    output_dir = json_directory()
#    callback_on_error = subtask(task=del_file_on_error, args=(sha1,))
#    try :
#        t1 = _compute_scores.delay(path, sha1, output_dir, callback=subtask(_jsonify_signal),
#                                     callback_on_error=callback_on_error)
#    except Exception as e:
#        etype, value, tb = sys.exc_info()
#        traceback.print_exception(etype, value, tb)
#        if callback_on_error :
#            subtask(callback_on_error).delay([e], sha1)
#        raise e
#    return t1

#def _features(path, sha1, name):
#    '''
#    Task for a ``feature`` database.
#    @return the subtask associated
#    '''
#    output_dir = json_directory()
#    callback_on_error = subtask(task=del_file_on_error, args=(sha1,))
#    try :
#        t1 = _jsonify_features.delay(path, name, sha1, output_dir, '/data/jbrowse', '', False,
#                            callback_on_error=callback_on_error)
#    except Exception as e:
#        etype, value, tb = sys.exc_info()
#        traceback.print_exception(etype, value, tb)
#        if callback_on_error :
#            subtask(callback_on_error).delay([e], sha1)
#        raise e
#    return t1


#def _relational(path, sha1, name):
#    '''
#    Task for a ``relational`` database
#    @return the subtask associated
#    '''
#    output_dir = json_directory()
#    callback_on_error = subtask(task=del_file_on_error, args=(sha1,))
#    try :
#        t1 = _jsonify_features.delay(path, name, sha1, output_dir, '/data/jbrowse', '', True,
#                    callback_on_error=callback_on_error)
#        print t1.task_id
#    except Exception as e:
#        etype, value, tb = sys.exc_info()
#        traceback.print_exception(etype, value, tb)
#        if callback_on_error :
#            subtask(callback_on_error).delay([e], sha1)
#        raise e
#    return t1





#
#'''
#_sql_dispatch : will choose in which process the database will go, based on it's datatype
#'''
#
#_sql_dispatch = {'quantitative' : lambda *args, **kw : _signal(*args, **kw),
#                 constants.SIGNAL : lambda *args, **kw : _signal(*args, **kw),
#
#                 'qualitative' :  lambda *args, **kw : _features(*args, **kw),
#                 constants.FEATURES :  lambda *args, **kw : _features(*args, **kw),
#
#                 'extended' :  lambda *args, **kw : _relational(*args, **kw),
#                  constants.RELATIONAL :  lambda *args, **kw : _relational(*args, **kw)
#                  }






#### GFEATMINER ####
import gMiner

@task()
def gfeatminer_request(user_id, project_id, req, job_description, job_name):
    '''
    Launch a gFeatMiner request.
    '''
    print 'gfeatminer request %s : ' % req
    try :
        
        data = gMiner.run(**req)
        print 'gMiner ended with %s ' % data
        for path in data:
            if os.path.splitext(path)[1] == '.sql':
                session = model.DBSession()
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
        session.close()







### TRACK PROCESSING ###




@task()
def process_track(user_id, **kw):
    '''
    Entry point for uploading and processing tracks.
    '''
   
        
    if not 'assembly' in kw and not 'project_id' in kw:
        raise Exception('Missing assembly parameters.')
    assembly_id = kw.get('assembly', None)
    
    files = util.upload(**kw)
        
    if files is None:
        raise 'No files to upload'
    
    
    project = None
    session = model.DBSession()
    
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
            from pygdv.handler.track import create_track
            kw['extension'] = extension
            kw['admin'] = admin
            task_id, track_id = create_track(user_id, sequence, f=f.name, trackname=filename, project=project, session=session, **kw)
            
            if task_id == constants.NOT_SUPPORTED_DATATYPE or task_id == constants.NOT_DETERMINED_DATATYPE:
                raise Exception('format %s' % task_id)
            
    except Exception as e:
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
        session.rollback()        
        raise e
    
    finally:
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
        del_input.delay(sha1)
        raise e

@task()
def process_text_file(datatype, assembly_name, path, sha1, name, _format, tmp_file, destination):
    '''
    Entry point of the text file.
    '''
    try :
        convert(path, destination, sha1, datatype, assembly_name, name, tmp_file, _format)
        dispatch = _sqlite_dispatch.get(datatype)
        dispatch(destination, sha1, name)
    except Exception as e:
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
        del_input.delay(sha1)
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




 
