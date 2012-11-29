from __future__ import absolute_import
'''
Tracks handler.
'''

from pygdv.model import DBSession, Track
import os
import shutil
import tg
from pygdv.lib import constants
import transaction

DEBUG_LEVEL = 0


def debug(s, t=0):
    if DEBUG_LEVEL > 0:
        print '[track handler] %s%s' % ('\t' * t, s)


def delete_input(sha1):
    '''
    Delete the input with the sha1 specified.
    Must delete in the "track directory" + '.sql' and
    in the "json directory"
    :param sha1 : the sha1 of the input
    '''
    if sha1 is not None:
        trackdir = os.path.join(constants.storage['data']['sql'], sha1)
        shutil.rmtree(trackdir)
        for v in constants.visualisations_list:
            shutil.rmtree(os.path.join(constants.jsons_store_path, v, sha1), ignore_errors=True)


def delete_track(track=None, track_id=None):
    '''
    Delete the track and the input associated if this is the only track with this input.
    '''
    if track is None:
        track = DBSession.query(Track).filter(Track.id == track_id).first()
    if track is None:
        return
    _input = track.input
    if _input is not None:
        if len(_input.tracks) == 1:
            delete_input(_input.sha1)
            DBSession.delete(_input)
    DBSession.delete(track)
    DBSession.flush()


def link(track):
    return tg.config.get('main.proxy') + tg.url('/tracks/link?track_id=%s' % track.id)


def plugin_link(track):
    return tg.config.get('main.proxy') + tg.url('/') + track.rel_path


def edit(track=None, track_id=None, name=None, color=None):
    if track is None:
        track = DBSession.query(Track).filter(Track.id == track_id).first()
    debug('edit track %s' % track)
    if name is not None:
        track.name = name
    if color is not None:
        p = dict(track.parameters)
        if track.parameters is None:
            p = {'color': color}
        else:
            p.update({'color': color})
        track.parameters = p
    DBSession.flush()
