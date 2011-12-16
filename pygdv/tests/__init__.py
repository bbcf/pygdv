from pygdv.lib import constants, util
import os, random, string


test_dir = constants.test_dir


tmp_dir = os.path.join(test_dir, 'tmp')
test_file_dir = os.path.join(test_dir, 'test_files')



files = {}


files['feature']= os.path.join(test_file_dir, 'feature.sql')
files['signal']= os.path.join(test_file_dir, 'signal.sql')
files['relational']= os.path.join(test_file_dir, 'relational.sql')

files['feature_r']= os.path.join(test_file_dir, 'feature.result')
files['signal_r']= os.path.join(test_file_dir, 'signal.result')
files['relational_r']= os.path.join(test_file_dir, 'relational.result')


random_name = lambda x: ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(x))



def assertFileEquals(f1, f2):
    sha1 = util.get_file_sha1(os.path.abspath(f1))
    sha2 = util.get_file_sha1(os.path.abspath(f2))
    return sha1 == sha2