import tempfile
import tg
import os
from pkg_resources import resource_filename


def temporary_directory():
    root = None
    if 'temporary.directory' in tg.config:
        root = tg.config.get('temporary.directory')
    else:
        root = os.path.join(resource_filename('pygdv', 'tmp'))
    return tempfile.mkdtemp(dir=root)


def download_file_field(file_field, to):
    with open(to, 'wb') as outf:
        file_value = file_field.value
        outf.write(file_value)
        outf.close()


class FileInfo(object):
    """
    Dummy object to store information about a file (uploaded, paths, ...)
    """
    def __init__(self, inputtype, inpath, trackname, extension, outpath, admin):
        self.inputtype = inputtype
        self.paths = {
            'in': inpath,
            'upload_to': outpath
        }
        self.trackname = trackname
        self.uploaded = False
        self.admin = admin

    def __repr__(self):
        return """<fi> intype: %s | name: %s | uploaded: %s | admin: %s
        paths: %s
        """ % (self.inputtype, self.trackname, self.uploaded, self.admin, ' | '.join(['%s : %s' % (k, v) for k, v in self.paths.iteritems()]))
