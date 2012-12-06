from pkg_resources import resource_filename
import os
from tg import url
import tg
from pygdv import PROJECT_ROOT


data_store_path = os.path.join(PROJECT_ROOT, 'public', 'data')
tracks_store_path = os.path.join(data_store_path, 'tracks')
jsons_store_path = os.path.join(data_store_path, 'jbrowse')

storage = {
    'data': {
        'sql': os.path.join(tracks_store_path, 'sql'),
        'bam': os.path.join(tracks_store_path, 'bam')
    },
    'vizu': {
        'signal': os.path.join(jsons_store_path, 'signal'),
        'relational': os.path.join(jsons_store_path, 'relational'),
        'features': os.path.join(jsons_store_path, 'features'),
        'bam_coverage': os.path.join(jsons_store_path, 'bam_coverage'),
    },
    'bioscript': os.path.join(data_store_path, 'bioscript')
}


bin_directory_path = os.path.join(PROJECT_ROOT, 'bin')

visualisations_list = ['signal', 'relational', 'features']
vizualisations = {
    'signal': ['signal'],
    'relational': ['relational'],
    'features': ['features'],
    'bam': ['bam_coverage', 'bam_feature']
}


mother_dir = 'pygdv'
bin_dir = 'bin'
test_dir = 'tests'
data_dir = 'pygdv.public.data'
json_dir = 'jbrowse'
tracks_dir = 'tracks'
plugin_dir = 'plugins'
extra_dir = 'extras'

# STATUSES
PENDING = 'PENDING'
SUCCESS = 'SUCCESS'
ERROR = 'FAILURE'
RUNNING = 'RUNNING'

default_track_color = 'red'

# IMAGES TYPES IN GDV
FEATURE_TRACK = 'FeatureTrack'
IMAGE_TRACK = 'ImageTrack'

track_types = ['track', 'bed', 'wig', 'gff', 'gtf', 'bedgraph']
# DATA DIRECTORIES





def admin_user_email():
    return tg.config.get('admin.user.email')


def admin_user_key():
    return tg.config.get('admin.user.key')

admin_user = {
    'id': 1,
    'firstname': 'user',
    'name': 'admin',
}


def temporary_directory():
    if 'temporary.directory' in tg.config:
        return tg.config.get('temporary.directory')
    else:
        return os.path.join(resource_filename('pygdv', 'tmp'))



def extra_url():
    return url('/data/extras')


def bin_directory():
    return os.path.join(resource_filename(mother_dir, bin_dir))


def callback_track_url():
    return tg.config.get('main.proxy') + url('/tracks')


# URLS TO PUT IN JSON
def data_root():
    return url('/data/jbrowse/')


def style_root():
    return url('/css/')


def image_root():
    return url('/img/')


track_data = 'trackData.json'


# TRACKS TYPES
NOT_DETERMINED_DATATYPE = 'not determined'
RELATIONAL = 'relational'
SIGNAL = 'signal'
FEATURES = 'features'
NOT_SUPPORTED_DATATYPE = 'format not supported'

# DATA FORMAT
date_format = "%d. %b %Y %Hh%M"

tiny_date_format = "%d/%m/%y"

rights = {
    'upload': {'id': 1, 'name': 'Upload', 'desc': 'A group with this permission can upload tracks to the project and execute jobs on the web interface.'},
    'download': {'id': 2, 'name': 'Download', 'desc': 'A group with this permission can download files on a project.'},
    'read': {'id': 3, 'name': 'Read', 'desc': 'A group with this permission can view the project.'}
}

permissions = {
    'admin': {'id': 1, 'name': 'admin', 'desc': 'This permission give admin right to the bearer.'},
    'read': {'id': 2, 'name': 'read', 'desc': 'This permission give read right to the bearer.'}
}

groups = {
    'admin': {'id': 1, 'name': 'Admins'},
    'user': {'id': 2, 'name': 'Users'},
}

right_upload = rights['upload']['name']
right_download = rights['download']['name']
right_read = rights['read']['name']

right_upload_id = rights['upload']['id']
right_download_id = rights['download']['id']
right_read_id = rights['read']['id']

group_admins = groups['admin']['name']
group_admins_id = groups['admin']['id']
perm_admin = permissions['admin']['name']

group_users = groups['user']['name']
group_users_id = groups['user']['id']
perm_user = permissions['read']['name']

tmp_user_name = 'user-not-registered'


full_rights = {right_read: True, right_download: True, right_upload: True}


formats_export = ('sqlite', 'wig', 'bed', 'gtf')

formats_supported = ('GFF', 'GTF', 'WIG', 'BED', 'BEDGRAPH')


REQUEST_TYPE = 'REQUEST_CLASSIFIER'
REQUEST_TYPE_COMMAND_LINE = 'command_line'
REQUEST_TYPE_BROWSER = 'browser'


JOB_IMAGE = 'job_image'
JOB_TRACK = 'job_track'
JOB_FAILURE = 'job_failure'
JOB_PENDING = 'job_pending'

job_output_reload = JOB_TRACK
job_output_image = JOB_IMAGE


