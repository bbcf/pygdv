from pkg_resources import resource_filename
import os
from tg import url
import tg

mother_dir = 'pygdv'
bin_dir = 'bin'
test_dir = 'tests'
data_dir = 'pygdv.public.data'
json_dir = 'jbrowse'
tracks_dir = 'tracks'
plugin_dir = 'plugins'
extra_dir = 'extras'

public_user_email = 'webmaster.bbcf@epfl.ch'
# STATUSES
PENDING = 'PENDING'
SUCCESS = 'SUCCESS'
ERROR = 'FAILURE'
RUNNING = 'RUNNING'

default_track_color = 'red'

# IMAGES TYPES IN GDV
FEATURE_TRACK = 'FeatureTrack'
IMAGE_TRACK = 'ImageTrack'

# DATA DIRECTORIES
def json_directory():
    return os.path.join(resource_filename(data_dir, json_dir))



def temporary_directory():
    if 'temporary.directory' in tg.config:
        return tg.config.get('temporary.directory')
    else :
        return os.path.join(resource_filename('pygdv', 'tmp'))



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



right_upload = 'Upload'
right_download = 'Download'
right_read = 'Read'

right_upload_id = 3
right_download_id = 2
right_read_id = 1

group_admins = 'Admins'
group_admins_id = 1
perm_admin = 'admin'

group_users = 'Users'
group_users_id = 2
perm_user = 'user'

tmp_user_name = 'user-not-registered'



full_rights = {right_read : True, right_download : True, right_upload : True}


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


