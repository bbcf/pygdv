from celery.task import task, chord, subtask, TaskSet
import shutil, os
from pygdv.lib.jbrowse import jsongen, scores
from pygdv.lib.constants import json_directory
from celery.result import AsyncResult

success = 1


#############################################################################################################
#        FILE PROCESSING
#############################################################################################################

@task()
def del_file_on_error(tasks, sha1, output_dir, *args, **kw):
    print args
    print kw
    '''
    Verify if the file are well processed.
    If no, it will erase the directory created in the
    tracks directory
    @param tasks : a list of return result. If one is different from 1, the directory is erased.
    '''
    print 'del file on error tasks :%s, sha1 : %s, output_dir : %s' % (tasks, sha1, output_dir)
    for id in tasks:
        if not id == success :
            shutil.rmtree(os.path.join(output_dir, sha1))
            raise id


@task()
def process_signal2(database, sha1):
    '''
    Process a ``signal`` SQL file and create the databases needed by JBrowse.
    @param database : the database
    @param sha1 : the sah1 of the file
    '''
    output_dir = json_directory()
    callback = subtask(task=del_file_on_error, args=(sha1, output_dir))
    print 'process signal db : %s, sha1 : %s' % (database, sha1)
    
    
    job = TaskSet(tasks=[
        _compute_scores.subtask((database, sha1, output_dir)),
        _jsonify_signal.subtask((sha1, output_dir, database))
                         ])
    
    print job
    return job




def process_signal(database, sha1):
    '''
    Process a ``signal`` SQL file and create the databases needed by JBrowse.
    @param database : the database
    @param sha1 : the sah1 of the file
    '''
    output_dir = json_directory()
    callback = subtask(task=del_file_on_error, args=(sha1, output_dir))
    
    t1 = _compute_scores.subtask((database, sha1, output_dir))
    t2 = _jsonify_signal.subtask((sha1, output_dir, database))
    job = chord(tasks=[
        t1,t2
                         ])(callback)
    return job  

@task()
def process_features(database, sha1, name, extended = False): 
    '''
    Process a ``features`` SQL file and create the databases needed by JBrowse.
    @param database : the database
    @param sha1 : the sah1 of the file
    @param name : the name of the output track
    @param extended : if the SQLite database is 'extended' format
    '''
    output_dir = json_directory()
    callback = subtask(task=del_file_on_error, args=(sha1, output_dir))
    job = chord(tasks = [
            _jsonify_features.subtask(database, name, sha1, output_dir, 'public_url', 'browser_url', extended)
                   ])(callback)
    return job





@task()
def _compute_scores(database, sha1, output_dir):
    '''
    Launch the process to precalculate scores on a signal database.
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
def _jsonify_features(database, name, sha1, output_dir, public_url, browser_url, extended):
    '''
    Launch the process to produce a JSON output for a ``feature`` database.
    '''
    jsongen.jsonify(database, name, sha1, output_dir, public_url, browser_url, extended)
    return 1







