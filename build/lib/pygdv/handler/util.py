import os,uuid,errno
from pkg_resources import resource_filename
from tg import app_globals as gl

def to_datagrid(grid_type, grid_data, grid_title, grid_display):
    '''
    Special method which format the parameters to fit
    on the datagrid template.
    @param grid_type : The DataGrid.
    @type grid_type : a DataGrid Object
    @param grid_data : The data.
    @type grid_data : a list of Object to fill in the DataGrid.
    @param grid_title : DataGrid title
    @type grid_title : A string.
    @param grid_display :True if the DataGrid has to be displayed.
    @type grid_display : a boolean. (Normally it's the len() of the 'grid_data' )
    '''
    data = {'grid':grid_type, 
    'grid_data':grid_data, 
    'grid_title':grid_title, 
    'grid_display':grid_display}
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
