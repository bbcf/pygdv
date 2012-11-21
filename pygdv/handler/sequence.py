from pygdv.lib import filemanager, constants
from pygdv.worker import tasks
from bbcflib.genrep import Assembly
from pygdv.model import DBSession, User, Track
import os


def add_new_sequence(sequence):
    '''
    Method called when a new sequence is created on GDV.
    It should import fast from JBrowse
    '''
    print 'add new sequence'
    file_url = Assembly(sequence).get_sqlite_url()
    print file_url
    out = os.path.join(filemanager.temporary_directory(), 'Genes.sql')
    fileinfo = filemanager.FileInfo(inputtype='url',
        inpath=file_url, trackname='Genes', extension='sql', outpath=out, admin=True)
    print fileinfo
    user = DBSession.query(User).filter(User.key == constants.admin_user_key()).first()
    user_info = {'id': user.id, 'name': user.name, 'email': user.email}
    sequence_info = {'id': sequence.id, 'name': sequence.name}

    # track
    t = Track()
    t.name = fileinfo.trackname
    t.sequence_id = sequence.id
    t.user_id = user.id
    DBSession.add(t)
    DBSession.flush()
    # send task
    async = tasks.new_input.delay(user_info, fileinfo, sequence_info, t.id)
    t.task_id = async.task_id
    DBSession.add(t)

    sequence.default_tracks.append(t)
    DBSession.add(sequence)
    DBSession.flush()
