from pygdv import model
from pygdv.lib import constants
from sqlalchemy.sql import and_, not_
import json, datetime, shutil, os


def new_tmp_job(name, user_id, project_id, session=None):
    dt = datetime.datetime.now().strftime(constants.date_format)
    if session is None:
        session = model.DBSession
        
    job = model.Job()
    job.name = name
    job.description = 'Launched the : ' + str(dt)
    job.user_id = user_id
    job.project_id = project_id
    job.output = constants.JOB_PENDING
    job.task_id = ''
    session.add(job)
    session.flush()
    return job

def update_job(job, name, description, user_id, project_id, output, task_id, sha1=None, session=None):
    if session is None:
        session = model.DBSession
    job.name = name
    job.description = description
    job.user_id = user_id
    job.project_id = project_id
    job.output = output
    job.task_id = task_id
    if sha1:
        job.data = sha1
    session.add(job)
    session.flush()
    return job
    

def new_job(name, description, user_id, project_id, output, task_id, sha1=None, session=None):
    if session is None:
        session = model.DBSession
    job = model.Job()
    job.name = name
    job.description = description
    job.user_id = user_id
    job.project_id = project_id
    job.output = output
    job.task_id = task_id
    if sha1:
        job.data = sha1
    session.add(job)
    session.flush()
    return job



def jobs(project_id):
    jobs = model.DBSession.query(model.Job).filter(and_(model.Job.project_id == project_id, not_(model.Job.output == constants.job_output_reload))).all()
    out = [{'id' : job.id,
            'name' : job.name,
            'description' : job.description,
            'output' : job.output} for job in jobs]
    
    return json.dumps({'jobs' : out})

def delete(job_id):
    job = model.DBSession.query(model.Job).filter(model.Job.id == job_id).first()
    if job is not None:
        try :
            path = os.path.join(constants.extra_directory(), job.data)
            os.remove(path)
        except (OSError, AttributeError):
            pass
        model.DBSession.delete(job)
        model.DBSession.flush()

#def new_sel(user_id, project_id, job_description, job_name, task_id=None):
#    job = Job()
#    
#    job.name = job_name
#    job.description = job_description
#    job.project_id = project_id
#    job.user_id = user_id
#    job.output = constants.job_output_reload
#    if task_id is not None:
#        job.task_id = task_id
#    DBSession.add(job)
#    DBSession.flush()
#    return job.id
#    
#    
#    
#def new_job(user_id, project_id, job_description, job_name, data, *args, **kw):
#    job = Job()
#    
#    job.name = job_name
#    job.description = job_description
#    job.project_id = project_id
#    job.user_id = user_id
#    if job.description == 'desc_stat' :
#        job.output = constants.job_output_image
#    else :#def new_sel(user_id, project_id, job_description, job_name, task_id=None):
#    job = Job()
#    
#    job.name = job_name
#    job.description = job_description
#    job.project_id = project_id
#    job.user_id = user_id
#    job.output = constants.job_output_reload
#    if task_id is not None:
#        job.task_id = task_id
#    DBSession.add(job)
#    DBSession.flush()
#    return job.id
#    
#    
#    
#def new_job(user_id, project_id, job_description, job_name, data, *args, **kw):
#    job = Job()
#    
#    job.name = job_name
#    job.description = job_description
#    job.project_id = project_id
#    job.user_id = user_id
#    if job.description == 'desc_stat' :
#        job.output = constants.job_output_image
#    else :
#        job.output = constants.job_output_reload
#
#    DBSession.add(job)
#    DBSession.flush()
#    
#    # prepare gfeatminer directory to receive the result of the job
#    path = os.path.join(constants.gfeatminer_directory(), str(job.id))
#
#    data['output_location'] = path
#    os.mkdir(path)
#    
#    task = tasks.gfeatminer_request.delay(user_id, project_id, data, job_description, job_name)
#    job.task_id = task.task_id
#    
#    
#    return job.id
#
#
#
#def parse_args(data):
#    '''
#    Parse the arguments coming from the browser to give a suitable
#    request to gFeatMiner
#    '''
#    
#    # format booleans
#    if data.has_key('compare_parents' ): data['compare_parents' ] = bool(data['compare_parents'  ])
#    if data.has_key('per_chromosome'  ): data['per_chromosome'  ] = bool(data['per_chromosome'   ])
#    
#    
#    # format track paths
#    if data.has_key('filter') and data['filter']:
#        data['selected_regions'] = os.path.join(constants.track_directory(), data['filter'][0]['path'] + '.sql')
#        data.pop('filter')
#        
#    if data.has_key('ntracks'):
#        data.update(dict([('track' + str(i+1), os.path.join(constants.track_directory(), v['path'] + '.sql')) for i, v in enumerate(data['ntracks'])]))
#        data.update(dict([('track' + str(i+1) + '_name', v.get('name', 'Unamed')) for i,v in enumerate(data['ntracks'])]))
#        data.pop('ntracks')
#    # Unicode filtering #
#    
#    data = dict([(k.encode('ascii'),v) for k,v in data.items()])
#        job.output = constants.job_output_reload
#
#    DBSession.add(job)
#    DBSession.flush()
#    
#    # prepare gfeatminer directory to receive the result of the job
#    path = os.path.join(constants.gfeatminer_directory(), str(job.id))
#
#    data['output_location'] = path
#    os.mkdir(path)
#    
#    task = tasks.gfeatminer_request.delay(user_id, project_id, data, job_description, job_name)
#    job.task_id = task.task_id
#    
#    
#    return job.id
#
#
#
#def parse_args(data):
#    '''
#    Parse the arguments coming from the browser to give a suitable
#    request to gFeatMiner
#    '''
#    
#    # format booleans
#    if data.has_key('compare_parents' ): data['compare_parents' ] = bool(data['compare_parents'  ])
#    if data.has_key('per_chromosome'  ): data['per_chromosome'  ] = bool(data['per_chromosome'   ])
#    
#    
#    # format track paths
#    if data.has_key('filter') and data['filter']:
#        data['selected_regions'] = os.path.join(constants.track_directory(), data['filter'][0]['path'] + '.sql')
#        data.pop('filter')
#        
#    if data.has_key('ntracks'):
#        data.update(dict([('track' + str(i+1), os.path.join(constants.track_directory(), v['path'] + '.sql')) for i, v in enumerate(data['ntracks'])]))
#        data.update(dict([('track' + str(i+1) + '_name', v.get('name', 'Unamed')) for i,v in enumerate(data['ntracks'])]))
#        data.pop('ntracks')
#    # Unicode filtering #
#    
#    data = dict([(k.encode('ascii'),v) for k,v in data.items()])
    
 
    
    
