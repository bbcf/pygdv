from pygdv.lib.constants import track_directory
from pygdv.model import DBSession, Job, JobParameters
import os


def new_job(project_id, job_description, job_name, data, *args, **kw):
    job = Job()
    
    job.name = job_name
    job.description = job_description
    
    
#    _created = Column(DateTime, nullable=False, default=datetime.now)
#    status = Column(statuses, nullable=False)
#    
#    user_id = Column(Integer, ForeignKey('User.id', ondelete="CASCADE"), nullable=False)
#    
#    project_id = Column(Integer, ForeignKey('Project.id', ondelete="CASCADE"), nullable=True)
#    
#    #task_id = Column(Integer, ForeignKey('celery_taskmeta.id', ondelete="CASCADE"), nullable=False)
#    #task = relationship('Task', uselist=False, backref='job')
#    task_id = Column(VARCHAR(255), nullable=False)
#    task = relationship('Task', uselist=False, primaryjoin='Job.task_id == Task.task_id', foreign_keys='Task.task_id')
#    parameters = relationship('JobParameters', uselist=False, backref='job')
#    
    
    
    pass




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
    if data.has_key('filter'):
        data['selected_regions'] = os.path.join(track_directory(), data['filter'][0]['path'])
        data.pop('filter')
        
    if data.has_key('ntracks'):
        data.update(dict([('track' + str(i+1), os.path.join(track_directory(), v['path'])) for i, v in enumerate(data['ntracks'])]))
        data.update(dict([('track' + str(i+1) + '_name', v.get('name', 'Unamed')) for i,v in enumerate(data['ntracks'])]))
        data.pop('ntracks')
    # Unicode filtering #
    
    data = dict([(k.encode('ascii'),v) for k,v in data.items()])