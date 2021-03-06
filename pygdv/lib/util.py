import os
import uuid
import errno
from pkg_resources import resource_filename
import tempfile
import urllib2
import shutil
import hashlib
import tg
from urllib2 import HTTPError
from pygdv.lib import constants
from urlparse import urlparse


def to_datagrid(grid_type, grid_data, grid_title=None, grid_display=None):
    '''
    Special method which format the parameters to fit
    on the datagrid template.
    @param grid_type: The DataGrid.
    @type grid_type: a DataGrid Object
    @param grid_data: The data.
    @type grid_data: a list of Object to fill in the DataGrid
    @param grid_title: DataGrid title
    @type grid_title: A string.
    @param grid_display:True if the DataGrid has to be displayed.
    @type grid_display: a boolean. (Normally it's the len() of the 'grid_data' )
    '''
    data = {'grid': grid_type,
    'grid_data': grid_data}
    if grid_title is not None:
        data['grid_title'] = grid_title
    if grid_display is not None:
        data['grid_display'] = grid_display
    return data


def get_unique_tmp_directory():
    '''
    Return a String representation of the path to the
    'temporary' directory of GDV.
    This directory is unique, and is builded with this call.
    '''
    uid = str(uuid.uuid4())
    public_dirname = os.path.join(os.path.abspath(resource_filename(gl.tmp_pkg, uid)))
    try:
        os.mkdir(public_dirname)
    except OSError, e:
        if e.errno == errno.EEXIST:
                return get_unique_tmp_directory()
        else: #this error must be raised to tell that something wrong with mkdir
            raise OSError
    return public_dirname

block_sz = 8192


def upload(file_upload=None, url=None, fsys=None, extension=None, **kw):
    '''
    Upload the file and make it temporary.
    @param file_upload: if the file is uploaded from a FileUpload HTML field.
    @param url: if the file is uploaded from an url
    @param urls: a list of urls separated by whitespaces.
    @param fsys: if the file is on the same file system, a filesystem path
    @param fsys_list:  a list of fsys separated by whitespaces.
    @param file_names: a list of file name, in the same order than the files uploaded.
    If there is differents parameters given, the first file uploaded will be file_upload, 
    then urls, url, fsys and finally fsys_list
    @return a list of tuples: (filename, tmp_file, extension).
    '''
    files = []
    url = kw.get('urls', url)
    if file_upload is not None:
        filename = file_upload['filename']
        file_value = file_upload['value']
        tmp_file = tempfile.NamedTemporaryFile(suffix=filename, delete=False)
        tmp_file.write(file_value)
        tmp_file.close()
        files.append((kw.get('trackname', filename), tmp_file, extension))    
    
    if url is not None:
        u = urlparse(url)
        if u.hostname:
            filename, tmp_file = _download_from_url(u.geturl())
            if filename is not None:
                files.append((kw.get('trackname', filename), tmp_file, extension))
    return files
        
def _download_from_url(url, filename=None):
    '''
    Download a file from an url.
    @param url: the url
    @return a tuple: (filename, tmp_file).
    '''
    if filename is None:
        filename = url.split('/')[-1]
    try:
        u = urllib2.urlopen(url)
    
        
#    meta = u.info()
#    file_size = int(meta.getheaders("Content-Length")[0])
#    print "Downloading: %s Bytes: %s" % (filename, file_size)
        file_size_dl = 0
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=filename)
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buffer)
            tmp_file.write(buffer)
    #        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
    #        status = status + chr(8)*(len(status)+1)
    #        print status,
        tmp_file.close()
        return filename, tmp_file
    except HTTPError as e:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
        print '%s: %s' % (url, e)
        raise e


def str2bool(str):
    return str.lower() in ['true', 't', '1', 1, 'yes', 'y']

def get_file_sha1(file_path):
    '''                                                                                                                                                                                                    
    Get the sha1 hex digest of a file.                                                                                                                                                                     
    @param file_path: the absolute path to the file.   
    @return the sha1 digest en hexa                                                                                                                                             
    '''
    sha1 = hashlib.sha1()
    with open(file_path,'rb') as f:
        for chunk in iter(lambda: f.read(128*64), ''):
            sha1.update(chunk)
    return sha1.hexdigest()



def obfuscate_email(mail):
    '''
    Not really an obfuscator, but hide a part of the mail.
    Still readeable by user.
    '''
    start, end = mail.split('@')
    start_obfs = start[:-len(start)*10/100]
    end_obfs = end[:len(end)*100/100]
    return '%s..@%s..' % (start_obfs, end_obfs)
    
    
def get_directory(tag, filename):
    '''
    Get a pathname for the resource specified.
    @param tag: a string telling the path to get from ``pygdv.lib.app_globals``, representing the path were to put the file
    @param filename: the filename
    ''' 
    return resource_filename(getattr(gl, tag), filename)


def float_equals(a, b, epsilon=0.0000001):
    '''
    Look if two float are equals or not, with an epsilon error 
    '''
    return abs(a - b) < epsilon


import re
from sqlalchemy import asc, desc

def order_data(ordering, data):
    args = re.findall('(\+|\-){1}(\w+)+', ordering)
    od = {'+':[], '-':[]}
    for i in range(len(args)):
        tmp = args[i]
        sign = tmp[0]
        word = tmp[1]
        od[sign].append(word)
    data.order_by(asc(od['+']), desc(od['-']))



def file_upload_converter(kw):
    if 'file_upload' in kw:
        file_upload = kw['file_upload']
        if file_upload is not None:
            new_fu = {}
            new_fu['filename'] = file_upload.filename
            new_fu['value'] = file_upload.value
            kw['file_upload'] = new_fu



def tmpfile(prefix='', suffix='', delete=False):
    dir = tg.config.get('temporary.directory')
    return tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, dir=dir, delete=False)

def tmpdir():
    dir = constants.temporary_directory()
    return tempfile.mkdtemp(dir=dir)




def norm_url(url):
    if not url.startswith('http://'):
        url = 'http://%s' % url
    return url


def url_filename(url):
    u = urlparse(url)
    if not u.hostname:
        raise HTTPError('%s is not a valid URL.' % url)
    try:
        u = urllib2.urlopen(url)
        fname = u.info().get('Content-Disposition', None)
        if fname is not None:
            fname = fname.split('=')[1]
    except HTTPError:
        pass
    finally:
        u.close()
    if fname is None:
        fname = os.path.splitext(url.rsplit('/',1)[1])[0]
    return fname



block_sz = 8192
def download(url=None, file_upload=None, fsys=None, filename='noname', extension='noextension'):
    """
    Download the file to a temporary place
    """
    with open(os.path.join(tmpdir(), '%s.%s' % (filename, extension)), 'wb') as tmp_file:

        if file_upload is not None:
            #filename = file_upload.filename
            file_value = file_upload.value
            tmp_file.write(file_value)
            tmp_file.close()
            return tmp_file

        elif url is not None:
            url = norm_url(url)
            try:
                u = urllib2.urlopen(url)
                while True:
                    buffer = u.read(block_sz)
                    if not buffer: break
                    tmp_file.write(buffer)
                tmp_file.close()
                return tmp_file
            except HTTPError as e:
                print '%s: %s' % (url, e)
                raise e

        elif fsys is not None:
            tmp_file.close()
            shutil.copy(fsys, tmp_file.name)
            return tmp_file

        raise Exception("Nothing to download")


compressed_files_extensions = ('.gz', '.zip', '.tar', '.tgz', '.targz', '.txt.gz', '.tar.gz')

def is_compressed(extension):
    if not extension.startswith('.'): extension = '.%s' % extension
    return any(extension.lower().endswith(ext) for ext in compressed_files_extensions)
