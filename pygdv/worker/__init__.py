import os
from pkg_resources import resource_filename
#
#os.environ['CELERY_CONFIG_MODULE'] = 'celerycconfig'
#import celery
#print dir(celery)
#
#if 'TEMPORARY_DIRECTORY' in conf:
#    temporary_directory = conf['TEMPORARY_DIRECTORY']
#else :
temporary_directory =  os.path.join(resource_filename('pygdv', 'tmp'))
