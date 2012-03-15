from pygdv.lib.plugin import OperationPlugin, retrieve_track
from yapsy.IPlugin import IPlugin
from pygdv.widgets.plugins import form
import gMiner



class TestImagePlugin(IPlugin, OperationPlugin):
    
    
    
    def title(self):  
        return 'Give me an image from that track'
    
    def path(self):
        return ['Statistics', 'good image for publication']
    
    def output(self):
        return form.ImageForm

    def process(self, **kw):
        t = retrieve_track(kw, kw['my_track'])
        per_chromosomes = kw.get('per_chromosomes')
        d = {'track1' : t.path,
                    'track1_name' : t.name,
                    'operation' : 'describe',
                    'characteristic' : 'base_coverage',
                    'per_chromosome' : per_chromosomes,
                    'output_location' : '/tmp/'
                    }
        r = gMiner.run(**d)
        print r
    

    
    
    

                        