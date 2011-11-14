from pygdv.lib import constants
from pygdv.model import DBSession, Job
from pygdv.celery import tasks
import os


def new_job(user_id, project_id, job_description, job_name, data, *args, **kw):
    job = Job()
    
    job.name = job_name
    job.description = job_description
    job.project_id = project_id
    job.user_id = user_id
    
    DBSession.add(job)
    DBSession.flush()

    data['output_location'] = os.path.join(constants.gfeatminer_directory(), job.id)
    
    task_id = tasks.gfeatminer_request.delay(data)
    job.task_id = task_id
    
    
    return job.id



def parse_args(data):
    '''
    Parse the arguments coming from the browser to give a suitable
    request to gFeatMiner
    '''
    print 'parse args %s' % data
    
    # format booleans
    if data.has_key('compare_parents' ): data['compare_parents' ] = bool(data['compare_parents'  ])
    if data.has_key('per_chromosome'  ): data['per_chromosome'  ] = bool(data['per_chromosome'   ])
    
    
    # format track paths
    if data.has_key('filter') and data['filter']:
        data['selected_regions'] = os.path.join(constants.track_directory(), data['filter'][0]['path'])
        data.pop('filter')
        
    if data.has_key('ntracks'):
        data.update(dict([('track' + str(i+1), os.path.join(constants.track_directory(), v['path'])) for i, v in enumerate(data['ntracks'])]))
        data.update(dict([('track' + str(i+1) + '_name', v.get('name', 'Unamed')) for i,v in enumerate(data['ntracks'])]))
        data.pop('ntracks')
    # Unicode filtering #
    
    data = dict([(k.encode('ascii'),v) for k,v in data.items()])