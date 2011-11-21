from pygdv.lib import constants
from pygdv.model import DBSession, Job, Project
from pygdv.celery import tasks
import os
import pygdv



def new_sel(user_id, project_id, job_description, job_name, task_id=None):
    job = Job()
    
    job.name = job_name
    job.description = job_description
    job.project_id = project_id
    job.user_id = user_id
    job.output = constants.job_output_reload
    if task_id is not None:
        job.task_id = task_id
    DBSession.add(job)
    DBSession.flush()
    return job.id
    
    
    
def new_job(user_id, project_id, job_description, job_name, data, *args, **kw):
    job = Job()
    
    job.name = job_name
    job.description = job_description
    job.project_id = project_id
    job.user_id = user_id
    if job.description == 'desc_stat' :
        job.output = constants.job_output_image
    else :
        job.output = constants.job_output_reload

    DBSession.add(job)
    DBSession.flush()
    
    # prepare gfeatminer directory to receive the result of the job
    path = os.path.join(constants.gfeatminer_directory(), str(job.id))

    data['output_location'] = path
    os.mkdir(path)
    
    task = tasks.gfeatminer_request.delay(user_id, project_id, data, job_description, job_name)
    job.task_id = task.task_id
    
    
    return job.id



def parse_args(data):
    '''
    Parse the arguments coming from the browser to give a suitable
    request to gFeatMiner
    '''
    
    # format booleans
    if data.has_key('compare_parents' ): data['compare_parents' ] = bool(data['compare_parents'  ])
    if data.has_key('per_chromosome'  ): data['per_chromosome'  ] = bool(data['per_chromosome'   ])
    
    
    # format track paths
    if data.has_key('filter') and data['filter']:
        data['selected_regions'] = os.path.join(constants.track_directory(), data['filter'][0]['path'] + '.sql')
        data.pop('filter')
        
    if data.has_key('ntracks'):
        data.update(dict([('track' + str(i+1), os.path.join(constants.track_directory(), v['path'] + '.sql')) for i, v in enumerate(data['ntracks'])]))
        data.update(dict([('track' + str(i+1) + '_name', v.get('name', 'Unamed')) for i,v in enumerate(data['ntracks'])]))
        data.pop('ntracks')
    # Unicode filtering #
    
    data = dict([(k.encode('ascii'),v) for k,v in data.items()])
    
    
def parse_response(user_id, project_id, data, job_description, job_name):
    for path in data:
        if os.path.splitext(path) == '.sql':
            project = DBSession.query(Project).filter(Project.id == project_id).first()
            rev = pygdv.handler.track.create_track(user_id, project.sequence, f=path, trackname='%s %s' 
                                         % (job_name, job_description), project=project)
    
    
    
    