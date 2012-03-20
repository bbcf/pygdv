import hashlib, os
from pygdv.lib import constants, util

root_key = 'Operations'





def new_track(_private_params=None, _file=None, trackname=None, **kw):
    '''
    Create a new track in GDV.
    param _file : the track path
    param trackname : the name of the track
    '''
    from pygdv.handler.track import create_track
    from pygdv.handler.job import new_job
    if _private_params is not None:
        session = _private_params['session']
        project = _private_params['project']
        task_id, track = create_track(_private_params['user_id'],project.sequence, 
                                      f=_file, trackname=trackname, project=project, session=session)
        return new_job('new track', kw.get('description'), project.user_id, project.id, constants.JOB_TRACK, task_id, session=session)
        
def new_file(_private_params, _file, description, **kw):
    '''
    Create a new file in GDV.
    param _file : the file path
    param name : the file name
    '''
    from pygdv.handler.job import new_job
    from pygdv.celery import tasks
    if _private_params is not None:
        project = _private_params['project']
        session = _private_params['session']
        sha1 = util.get_file_sha1(_file)
        path_to = os.path.join(constants.extra_directory(), sha1)
        task = tasks.copy_file.delay(_file, path_to)
        return new_job('new file', description, project.user_id, 
                       project.id, constants.JOB_IMAGE, task.task_id, sha1=sha1, session=session)



def retrieve_sequence(_private_params=None):
    '''
    Retrieve the sequence from the plugin 'process' method.
    '''
    if _private_params is not None:
        project = _private_params['project']
        return project.sequence


def retrieve_project(_private_params=None):
    '''
    Retrieve the project from the plugin 'process' method.
    '''
    if _private_params is not None:
        return _private_params['project']


def retrieve_track(_private_params=None, track_id=None):
    '''
    Retrieve the track from the plugin 'process' method.
    '''
    if _private_params is not None:
        project = _private_params['project']
        for track in project.tracks:
            if track.id == int(track_id):
                return track












class OperationPlugin(object):
    
    uid = None
    '''
    Inherit form this class to build your plugin.
    '''    
    def path(self):
        '''
        Here define the path of your plugin : the succession of buttons which leads to the form apparition.
        Must return a list. The root is %s.
        ex : return ['Statistics', 'Base Coverage']
        This list will result in three buttons (with %s as first), then 'Statistics' and 'Base Coverage' 
        the last that will make appears the form onClick.  
        ''' % (root_key, root_key)
        
        raise NotImplementedError('you must override this method in your plugin.')
    
    
    def title(self):
        '''
        Here you set the title of your form.
        ex : return 'My super title'
        '''
        
        raise NotImplementedError('you must override this method in your plugin.')
    
    def output(self):
        '''
        Here you must define the form to output when the user click on the last button you defined in the path property.
        The form are build using ToscaWidget0.9. 
        ex : 
        from pygdv.widgets.plugins import form
        return form.Example
        '''
        
        raise NotImplementedError('you must override this method in your plugin.')
        
    def process(self, **kw):
        '''
        Here you must define your function that will process the form parameters. 
        ex : a simple method that add two parameters :
        return kw.get('param1', 0) + kw.get('param2', 0)
        '''
        
        raise NotImplementedError('you must override this method in your plugin.')

    def description(self):
        '''
        Here you can give a description to your job.
        '''
        raise NotImplementedError('you must override this method in your plugin.')
    
    def unique_id(self):
        '''
        It's an unique identifier for your plugin.
        Do not override
        '''
        if not self.uid:
            self.uid = hashlib.sha1(self.path().__str__()).hexdigest()
        return self.uid
    
