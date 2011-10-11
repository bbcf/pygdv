from celery.task import task, TaskSet, chord, subtask
from tg import app_globals as gl
import shutil, os
from pygdv.lib.jbrowse import jsongen, scores

success = 1



@task()
def add(x, y):
    x = int(x)
    y = int(y)
    result = x + y
    
    return result


@task()
def div(x, y):
    return x/y

@task()
def callb(*args, **kw):
    print 'XXXXXXXXXXXXXXXXXXXXXXXXXXX'
    print args
    print kw
#    fg


@task()
def hellochord():
    cb = subtask(task=callb, kwargs={'sha1':'bloo'})
    job = chord(tasks = [
                   add.subtask((2,3)),
                   div.subtask((4,0))
                   ])(cb)
    print 'MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM'
    print job
    print dir(job)
    return job

@task()
def hellotakset():
    job = TaskSet(tasks = [
                add.subtask((2, 3)),
                div.subtask((4,0))
           ])
    res = job.apply_async()
    return res



def file_processing_callback(*args, **kw):
    '''
    Verify if the file are well processed.
    If no, it will erase the directory created in the
    tracks directory
    '''
    if not 'sha1' in kw or not 'output_dir' in kw:
        return
    for id in args:
        if not id == success :
            shutil.rmtree(os.path.join(kw ['output_dir'], kw['sha1']))
            return
    

#############################################################################################################
#        QUANTITATIVE PROCESSING
#############################################################################################################
def process_quantitative_file(database, sha1):
    '''
    Process a quantitative SQL file and create the databases needed by JBrowse.
    @param database : the database
    @param sha1 : the sah1 of the file
    '''
    output_dir = gl.json_dir
    callback = subtask(task=file_processing_callback, kwargs={'sha1':sha1, 'output_dir':output_dir})
    job = chord(tasks=[
        _compute_scores.subtask((database, sha1, output_dir)),
        _jsonify_quantitative.subtask(sha1, output_dir, database)
                         ])(callback)
    return job

@task()
def _compute_scores(database, sha1, output_dir):
    return scores.pre_compute_sql_scores(database, sha1, output_dir)

@task()
def _jsonify_quantitative(sha1, output_root_directory, database_path):
    return jsongen.jsonify_quantitative(sha1, output_root_directory, database_path)

#############################################################################################################
#        QUALITATIVE PROCESSING
#############################################################################################################
@task()
def process_qualitative_file(database, sha1, name, extended = False): 
    '''
    Process a quantitative SQL file and create the databases needed by JBrowse.
    @param database : the database
    @param sha1 : the sah1 of the file
    @param name : the name of the output track
    @param extended : if the SQLite database is 'extended' format
    '''
    output_dir = gl.json_dir
    return jsongen.jsonify(database, name, sha1, output_dir, 'public_url', 'browser_url', extended)







