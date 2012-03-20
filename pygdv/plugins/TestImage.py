from pygdv.lib.plugin import OperationPlugin, retrieve_track, new_file
from yapsy.IPlugin import IPlugin
from pygdv.widgets.plugins import form
import gMiner, string, random


random_name = lambda x : ''.join(random.choice(string.ascii_uppercase) for x in range(x))

class TestImagePlugin(IPlugin, OperationPlugin):
    
    
    
    def title(self):  
        return 'Give me an image from that track'
    
    def path(self):
        return ['Statistics', 'good image for publication']
    
    def output(self):
        return form.ImageForm

    def description(self):
        return 'This method compute the base coverage for the track selected'
    
    def process(self, **kw):
        t = retrieve_track(kw, kw['my_track'])
        per_chromosomes = kw.get('per_chromosomes')
        rname = random_name(7)
        
        d = {'track1' : t.path,
                    'track1_name' : t.parameters.label,
                    'operation' : 'describe',
                    'characteristic' : 'base_coverage',
                    'per_chromosome' : per_chromosomes,
                    'output_location' : '/tmp/',
                    'output_name' : rname
                    }
        result = gMiner.run(**d)
        for f in result:
            new_file(kw, f, self.description())
    

    
    
    

                        