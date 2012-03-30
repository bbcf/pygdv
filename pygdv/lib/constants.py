from pkg_resources import resource_filename
import os
from tg import url

mother_dir = 'pygdv'
bin_dir = 'bin'
test_dir = 'tests'
data_dir = 'pygdv.public.data'
json_dir = 'jbrowse'
tracks_dir = 'tracks'
plugin_dir = 'plugins'
extra_dir = 'extras'

public_user_email = 'public@pygdv.ch'
# STATUSES
PENDING = 'PENDING'
SUCCESS = 'SUCCESS'
ERROR = 'FAILURE'
RUNNING = 'RUNNING'


# IMAGES TYPES IN GDV
FEATURE_TRACK = 'FeatureTrack'
IMAGE_TRACK = 'ImageTrack'

# DATA DIRECTORIES
def json_directory():
    return os.path.join(resource_filename(data_dir, json_dir))


def track_directory():
    return os.path.join(resource_filename(data_dir, tracks_dir))

def extra_directory():
    return os.path.join(resource_filename(data_dir, extra_dir))

def extra_url():
    return url('/data/extras')

def gfeatminer_url():
    return url('/data/gfeatminer')


def bin_directory():
    return os.path.join(resource_filename(mother_dir, bin_dir))

def test_directory():
    return os.path.join(resource_filename(mother_dir, test_dir))

def plugin_directory():
    return os.path.join(resource_filename(mother_dir, plugin_dir))


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



right_upload = 'Upload'
right_download = 'Download'
right_read = 'Read'

right_upload_id = 3
right_download_id = 2
right_read_id = 1

group_admins = 'Admins'
perm_admin = 'admin'

group_users = 'Users'
perm_user = 'user'

tmp_user_name = 'tmp_user'



full_rights = {right_read : True, right_download : True, right_upload : True}


formats_export = ('tsv', 'sql', 'bed')




REQUEST_TYPE = 'REQUEST_CLASSIFIER'
REQUEST_TYPE_COMMAND_LINE = 'command_line'
REQUEST_TYPE_BROWSER = 'browser'



JOB_IMAGE = 'job_image'
JOB_TRACK = 'job_track'
JOB_FAILURE = 'job_failure'
JOB_PENDING = 'job_pending'

job_output_reload = JOB_TRACK
job_output_image = JOB_IMAGE


