from pygdv.tests import tmp_dir, files, random_name, assertFileEquals

import shutil, os

try:
    import unittest2 as unittest
except ImportError:
    import unittest

__test__ = True



from pygdv.lib.jbrowse import jsongen, scores

class TestJsonify(unittest.TestCase):
    
    
    def setUp(self):
        print '[x] setting up tests'
        self.remove_tmp_dir = True # True : remove all files resulting of the test at the end. False : keep them.
        
        try:
            os.mkdir(tmp_dir)
        except OSError:
            pass
        
    def test_jsonify(self):
        output_name = random_name(7)
        print '[t] jsonify feature to %s' % output_name
        jsongen.jsonify(files['feature'], 'aname', output_name, tmp_dir, 'pub_url', 'browser_url', False)
        self.assertTrue(assertFileEquals(files['feature'], output_name))
        
        output_name = random_name(7)
        print '[t] jsonify relational to %s' % output_name
        jsongen.jsonify(files['relational'], 'aname', output_name, tmp_dir, 'pub_url', 'browser_url', True)
        self.assertTrue(assertFileEquals(files['relational'], output_name))
        
        
        
    def tearDown(self):
        if self.remove_tmp_dir:
            print '[x] removing tmp directory : %s' % tmp_dir
            shutil.rmtree(tmp_dir, ignore_errors = True)