from pygdv import model
from pygdv.lib import constants
from sqlalchemy.sql import and_, not_
import json
import datetime
import os











def new_job(name, description, user_id, project_id, output, ext_task_id=None, task_id=None):
    job = model.Job()
    job.name = name
    job.description = description
    job.user_id = user_id
    job.project_id = project_id
    job.output = output
    if ext_task_id is not None:
        job.ext_task_id = ext_task_id
    if task_id is not None:
        job.task_id = task_id
    model.DBSession.add(job)
    model.DBSession.flush()
    return job





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


