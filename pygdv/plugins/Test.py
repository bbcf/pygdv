from pygdv.lib.plugin import OperationPlugin
from pygdv.widgets.plugins import form
from yapsy.IPlugin import IPlugin



class TestPlugin(IPlugin, OperationPlugin):
    
    
    
    def title(self):
        return 'My super title.'
    
    def path(self):
        return ['Statistics', 'Base Coverage']
    
    def output(self):
        return form.ExampleForm
    
    def process(self, **kw):
        return 0


  
