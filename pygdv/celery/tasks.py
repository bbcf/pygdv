from celery.task import task, chord, subtask, TaskSet
import shutil, os, sys, traceback
from pygdv.lib.jbrowse import jsongen, scores
from pygdv.lib.constants import json_directory, track_directory
from celery.result import AsyncResult

success = 1


#############################################################################################################
#        FILE PROCESSING
#############################################################################################################

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
            path1 = os.path.join(track_directory(), sha1)
            path2 = os.path.join(json_directory(), sha1)
            shutil.rmtree(path1, ignore_errors = True)
            shutil.rmtree(path2, ignore_errors = True)
            raise theid
    return 1





def process_signal(database, sha1, name):
    '''
    Process a ``signal`` SQL file and create the databases needed by JBrowse.
    @param database : the database
    @param sha1 : the sah1 of the file
    '''
    print '[t] starting task ``process signal`` : db (%s), sha1(%s), name(%s).' % (database, sha1, name)
    output_dir = json_directory()
    callback = subtask(task=del_file_on_error, args=(sha1, output_dir))
    
    t1 = _compute_scores.subtask((database, sha1, output_dir))
    t2 = _jsonify_signal.subtask((sha1, output_dir, database))
    
    job = chord(tasks=[t1,t2])(callback)
    return job  


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
def _compute_scores(database, sha1, output_dir):
    '''
    Launch the process to pre-calculate scores on a signal database.
    '''
    scores.pre_compute_sql_scores(database, sha1, output_dir)
    return 1


@task()
def _jsonify_signal(sha1, output_root_directory, database_path):
    '''
    Launch the process to produce a JSON output for a ``signal`` database.
    '''
    print 'jsonify signal sha1 : %s, output dir : %s, path : %s ' % (sha1, output_root_directory, database_path)
    jsongen.jsonify_quantitative(sha1, output_root_directory, database_path)
    return 1


@task()
def _jsonify_features(database, name, sha1, output_dir, public_url, browser_url, extended, callback=None):
    '''
    Launch the process to produce a JSON output for a ``feature`` database.
    '''
    try :
        jsongen.jsonify(database, name, sha1, output_dir, public_url, browser_url, extended)
    except Exception as e:
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
        if callback :
            return subtask(callback).delay([e], sha1)
    return 1






