import os,uuid,errno
from pkg_resources import resource_filename
from tg import app_globals as gl
import tempfile
import urllib2
import shutil
import hashlib
from tw.forms.fields import TextArea

def to_datagrid(grid_type, grid_data, grid_title = None, grid_display = None):
    '''
    Special method which format the parameters to fit
    on the datagrid template.
    @param grid_type : The DataGrid.
    @type grid_type : a DataGrid Object
    @param grid_data : The data.
    @type grid_data : a list of Object to fill in the DataGrid
    @param grid_title : DataGrid title
    @type grid_title : A string.
    @param grid_display :True if the DataGrid has to be displayed.
    @type grid_display : a boolean. (Normally it's the len() of the 'grid_data' )
    '''
    data = {'grid':grid_type, 
    'grid_data':grid_data}
    if grid_title is not None :
        data['grid_title'] = grid_title
    if grid_display is not None :
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
        else:#this error must be raised to tell that something wrong with mkdir
            raise OSError
    return public_dirname

block_sz = 8192

def upload(file_upload=None, urls=None, url=None, fsys=None, fsys_list=None, **kw):
    '''
    Upload the file and make it temporary.
    @param file_upload : if the file is uploaded from a FileUpload HTML field.
    @param url : if the file is uploaded from an url
    @param urls : a list of urls separated by whitespaces. 
    @param fsys : if the file is on the same file system
    @return a list of tuples : (filename, tmp_file).
    '''
    files = []  
    if file_upload is not None:
        filename = file_upload.filename
        file_value = file_upload.value
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.write(file_value)
        tmp_file.close()
        files.append((filename, tmp_file))
    
    if urls is not None: 
        for u in urls.split():
            files.append(_download_from_url(u))
    
    if url is not None:
        files.append(_download_from_url(url))
    
    if fsys is not None:
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        shutil.copyfile(fsys, tmp_file)
        files.append((fsys.split('/')[-1], tmp_file))
    
    if fsys_list is not None: 
        for f in fsys_list :
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
            shutil.copyfile(f, tmp_file)
            files.append((f.split('/')[-1], tmp_file))
        
    return files
        
def _download_from_url(url):
    '''
    Download a file from an url.
    @param url : the url
    @return a tuple : (filename, tmp_file).
    '''
    filename = url.split('/')[-1]
    u = urllib2.urlopen(url)
    
#    meta = u.info()
#    file_size = int(meta.getheaders("Content-Length")[0])
#    print "Downloading: %s Bytes: %s" % (filename, file_size)
    file_size_dl = 0
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
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



def get_file_sha1(file_path):
    '''                                                                                                                                                                                                    
    Get the sha1 hex digest of a file.                                                                                                                                                                     
    @param file_path : the absolute path to the file.   
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
    @param tag : a string telling the path to get from ``pygdv.lib.app_globals``, representing the path were to put the file
    @param filename : the filename
    ''' 
    return resource_filename(getattr(gl, tag), filename)


def float_equals(a, b, epsilon=0.0000001):
    '''
    Look if two float are equals or not, with an epsilon error 
    '''
    return abs(a - b) < epsilon
