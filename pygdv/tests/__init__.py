from pygdv.lib import constants, util
import os, random, string


test_dir = '.'#constants.test_dir


tmp_dir = os.path.join(test_dir, 'tmp')
test_file_dir = os.path.join(test_dir, 'test_files')



files = {}



files['gtf'] = os.path.join(test_file_dir, 'test.gtf')
files['bed'] = os.path.join(test_file_dir, 'test.bed')
files['bedgraph'] = os.path.join(test_file_dir, 'test.bedgraph')
files['wig'] = os.path.join(test_file_dir, 'test.wig')
files['feature'] = os.path.join(test_file_dir, 'feature.sql')
files['relational'] = os.path.join(test_file_dir, 'relational.sql')
files['signal'] = os.path.join(test_file_dir, 'signal.sql')

_formats = {'sql' : constants.NOT_DETERMINED_DATATYPE,
                    'bed' : constants.FEATURES,
                    'gff' : constants.RELATIONAL,
                    'gtf' : constants.RELATIONAL,
                    'bigWig' : constants.SIGNAL,
                    'wig' : constants.SIGNAL,
                    'bedgraph' : constants.SIGNAL
                    }

_datatypes = {      constants.FEATURES : constants.FEATURES,
                    'qualitative' : constants.FEATURES,
                    'QUALITATIVE' : constants.FEATURES,
                    constants.SIGNAL : constants.SIGNAL,
                    'quantitative' : constants.SIGNAL,
                    'QUANTITATIVE' : constants.SIGNAL,
                    constants.RELATIONAL : constants.RELATIONAL,
                    'qualitative_extended' : constants.RELATIONAL,
                    'QUALITATIVE_EXTENDED' : constants.RELATIONAL,
                    }

random_name = lambda x: ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(x))



def assertFileEquals(f1, f2):
    sha1 = util.get_file_sha1(os.path.abspath(f1))
    sha2 = util.get_file_sha1(os.path.abspath(f2))
    return sha1 == sha2