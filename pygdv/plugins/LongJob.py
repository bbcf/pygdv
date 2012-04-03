from pygdv.lib.plugin import OperationPlugin, new_track, retrieve_project, retrieve_sequence, retrieve_track
from pygdv.widgets.plugins import form
from yapsy.IPlugin import IPlugin
import track
import track.manipulate
import gMiner

import tempfile

class LongJob(IPlugin, OperationPlugin):
    
    
    
    def title(self):
        return 'Threshold'
    
    def path(self):
        return ['Manipulation', 'long job']
    
    def output(self):
        return form.ThresholdForm
    
    def description(self):
        return 'Apply a threshold on the track selected, but very long'
    
    def process(self, **kw):
        import time
        time.sleep(float(kw.get('thr', 5)))
        threshold = int(kw.get('thr', 0))
        my_track = retrieve_track(kw, kw.get('track'))
        
        t = track.manipulate.threshold(X=my_track.path, s=threshold)
        path = track.common.temporary_path(suffix='.sql')
        t.datatype = 'signal'
        t.export(path)
        
        
        # create a new track on GDV
        new_track(kw, path, self.title(), self.description())
        return 0



