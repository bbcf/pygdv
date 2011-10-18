from pkg_resources import resource_filename
import os

data_dir = 'pygdv.data'
json_dir = 'jbrowse'
tracks_dir = 'tracks'

# STATUSES
PENDING = 'PENDING'
SUCCESS = 'SUCCESS'
ERROR = 'FAILURE'
RUNNING = 'RUNNING'


def json_directory():
    return os.path.join(resource_filename(data_dir, json_dir))


def track_directory():
    return os.path.join(resource_filename(data_dir, tracks_dir))

