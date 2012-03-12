import uuid

root_key = 'Operation'

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
        

    
    def unique_id(self):
        '''
        It's an unique identifier for your plugin.
        '''
        if not self.uid:
            self.uid = uuid.uuid4()
        return self.uid.urn.split(':')[2]
    
