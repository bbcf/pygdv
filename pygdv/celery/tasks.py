from celery.task import task, TaskSet, chord, subtask
from tg import app_globals as gl
import shutil, os
from pygdv.lib.jbrowse import jsongen, scores
from pygdv.lib import util
from celery.result import AsyncResult

success = 1


#############################################################################################################
#        FILE PROCESSING
#############################################################################################################

@task()
def del_file_on_error(tasks, sha1, output_dir):
    '''
    Verify if the file are well processed.
    If no, it will erase the directory created in the
    tracks directory
    @param tasks : a list of return result. If one is different from 1, the directory is erased.
    '''
    for id in tasks:
        if not id == success :
            shutil.rmtree(os.path.join(output_dir, sha1))
            break

@task()
def process_signal(database, sha1):
    '''
    Process a ``signal`` SQL file and create the databases needed by JBrowse.
    @param database : the database
    @param sha1 : the sah1 of the file
    '''
    output_dir = gl.json_dir
    callback = subtask(task=del_file_on_error, args=(sha1, output_dir))
    job = chord(tasks=[
        _compute_scores.subtask((database, sha1, output_dir)),
        _jsonify_signal.subtask(sha1, output_dir, database)
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
    output_dir = gl.json_dir
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
    jsongen.jsonify_quantitative(sha1, output_root_directory, database_path)
    return 1


@task()
def _jsonify_features(database, name, sha1, output_dir, public_url, browser_url, extended):
    '''
    Launch the process to produce a JSON output for a ``feature`` database.
    '''
    jsongen.jsonify(database, name, sha1, output_dir, public_url, browser_url, extended)
    return 1







