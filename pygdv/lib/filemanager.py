import tempfile
import tg
import os
import urllib2
import shutil
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


def download_url(url, to, block_sz=2048 * 4):
        file_size_dl = 0
        stream = urllib2.urlopen(url)
        with open(to, 'wb') as outf:
            while True:
                buffer = stream.read(block_sz)
                if not buffer:
                    break
            file_size_dl += len(buffer)
            outf.write(buffer)


def download_fsys(infile, to):
    shutil.cp(infile, to)


class FileInfo(object):
    """
    Dummy object to store information about a file (uploaded, paths, ...)
    """
    def __init__(self, inputtype, inpath, trackname, extension, outpath, admin):
        self.inputtype = inputtype
        self.paths = {
            'in': inpath,
            'upload_to': outpath,
            'store': None
        }
        self.trackname = trackname
        self.extension = extension.lower()
        self.info = {}
        self.states = {
            'tmpdel': False,
            'instore': False,
            'tosql': False,
            'admin': admin,
            'uploaded': False
        }
        self.visualizations = []

    def download(self):
        """
        Download the file in the system.
        """
        if self.inputtype == 'fsys':
            download_fsys(self.paths['in'], self.paths['upload_to'])
            self.states['uploaded'] = True
        elif self.inputtype == 'url':
            download_url(self.paths['in'], self.paths['upload_to'])
            self.states['uploaded'] = True
        elif self.inputtype == 'file_upload':
            self.download_file_field(self.paths['in'], self.paths['upload_to'])
            self.states['uploaded'] = True

    def __repr__(self):
        return """<fi> intype: %s | name: %s | uploaded: %s | admin: %s
        paths: %s
        """ % (self.inputtype, self.trackname, self.uploaded, self.admin, ' | '.join(['%s : %s' % (k, v) for k, v in self.paths.iteritems()]))
