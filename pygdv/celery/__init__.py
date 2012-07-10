import os
from celery.conf import conf
from pkg_resources import resource_filename

os.environ['CELERY_CONFIG_MODULE'] = 'celeryconfig'


if 'TEMPORARY_DIRECTORY' in conf:
    temporary_directory = conf['TEMPORARY_DIRECTORY']
else :
    temporary_directory =  os.path.join(resource_filename('pygdv', 'tmp'))
