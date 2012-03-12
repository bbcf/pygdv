from pygdv.lib.plugin import OperationPlugin
from pygdv.widgets.plugins import form
from yapsy.IPlugin import IPlugin



class SecondPlugin(IPlugin, OperationPlugin):
    
    
    
    def title(self):
        return 'My super title.'
    
    def path(self):
        return ['Statistics', 'A sub category', 'a child']
    
    def output(self):
        return form.ExampleForm


  
