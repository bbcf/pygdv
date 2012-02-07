from pygdv.tests import tmp_dir, files, _formats, _datatypes

import shutil, os

try:
    import unittest2 as unittest
except ImportError:
    import unittest

__test__ = True



from pygdv.lib.jbrowse import jsongen, scores

class TestJsonify(unittest.TestCase):
    
    
    def setUp(self):
        print '[x] setting up tests [x]'
        self.remove_tmp_dir = True # True : remove all files resulting of the test at the end. False : keep them.
        
        try:
            os.mkdir(tmp_dir)
        except OSError:
            pass
    
        
    
    
    def test_create_track(self):
        import os
        from pygdv.lib import constants
        import track
        
        
        
        formats_to_test = ['bed', 'wig', 'bedgraph', 'gtf']
        assembly_name = 'mm9'
        datatype = constants.FEATURES
        print '[x] testing conversion text files to sql'
        for f in formats_to_test:
            print '[.]     %s' % f
            datatype = _formats.get(f)
            name = '%s.sql' % f
            dst = os.path.join(tmp_dir, name)
            track.convert(f and (files[f], f) or files[f], dst)
            with track.load(dst, 'sql', readonly=False) as t:
                t.datatype = datatype
                t.assembly = assembly_name
        print '[x] DONE'
        
        
        
        
    def test_jsonify(self):
        import subprocess
        print '[x] testing processing of sqlite files'
        tracks = ['feature', 'relational', 'signal']
        for t_name in tracks:
            dst = os.path.join(tmp_dir, t_name)
            os.mkdir(dst)
            if t_name == 'feature':
                print '[.]     feature'
                jsongen.jsonify(files[t_name], 'name', 'feature', dst, '/data/jbrowse', '', False)
            elif t_name == 'relational':
                print '[.]     relational'
                jsongen.jsonify(files[t_name], 'name', 'relational', dst, '/data/jbrowse', '', True)
            else:
                print '[.]    signal'
                bin_dir = '../bin'
                script = 'psd.jar'
                efile = os.path.join(bin_dir, script)
                p = subprocess.Popen(['java', '-jar', efile, files[t_name], 'signal', dst], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                result = p.wait()
                if result == 1:
                    err = ', '.join(p.stderr)
                    raise Exception(err)
                jsongen.jsonify_quantitative('signal', dst,  files[t_name])


#    '''        
#    out_name = '%s.%s' % (sha1, 'sql')
#    dst = os.path.join(track_directory(), out_name)
#    t = tasks.process_text_file.delay(datatype, assembly_name, path, sha1, name, _format, out_name, dst)
#    '''
    
        
        
    def tearDown(self):
        if self.remove_tmp_dir:
            print '[x] removing tmp directory : %s' % tmp_dir
            shutil.rmtree(tmp_dir, ignore_errors = True)
            
            
            