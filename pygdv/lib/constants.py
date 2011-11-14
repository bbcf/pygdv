from pkg_resources import resource_filename
import os

data_dir = 'pygdv.public.data'
json_dir = 'jbrowse'
tracks_dir = 'tracks'

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


# URLS TO PUT IN JSON
DATA_ROOT = '/data/jbrowse/'
STYLE_ROOT = '/css/'
IMAGE_ROOT = '/img/'

track_data = 'trackData.json'


# TRACKS TYPES
NOT_DETERMINED_DATATYPE = 'not determined'
RELATIONAL = 'relational'
SIGNAL = 'signal'
FEATURES = 'features'
NOT_SUPPORTED_DATATYPE = 'format not supported'

# DATA FORMAT
date_format = "%A %d. %B %Y %H.%M.%S"





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


