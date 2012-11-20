
from pygdv.model import DBSession, Project
from pygdv.lib.jbrowse import util as jb
from pygdv.lib import constants, plugin

import json
import tg
import os
from tg import url


def prepare_view(project_id, *args, **kw):
    from pygdv import handler

    # Get the project
    project = DBSession.query(Project).filter(Project.id == project_id).first()
    tracks = project.success_tracks

    for t in tracks:
        if t.parameters is None:
            t.parameters = {}
        if not 'url' in t.parameters:
            t.parameters.update({
                    'url': os.path.join(t.visualization, t.input.sha1, '{refseq}', constants.track_data),
                    'label': t.name,
                    'type': t.visualization == 'signal' and 'ImageTrack' or 'FeatureTrack',
                    'gdv_id': t.id,
                    'key': t.name,
                    'date': t.tiny_date
                })
            DBSession.add(t)
            DBSession.flush()
    seq = project.sequence
    default_tracks = seq.default_tracks
    all_tracks = tracks + default_tracks

    # Track names must be different
    trackNames = []
    for t in all_tracks:
        while t.name in trackNames:
            ind = 0
            while(t.name[-(ind + 1)].isdigit()):
                ind += 1
            cpt = t.name[-ind:]
            try:
                cpt = int(cpt)
            except ValueError:
                cpt = 0
            cpt += 1

            tmp_name = t.name
            if ind > 0:
                tmp_name = t.name[:-ind]
            t.name = tmp_name + str(cpt)

        t.accessed
        DBSession.add(t)
        DBSession.flush()
        trackNames.append(t.name)

    # prepare javascript parameters
    refSeqs = 'refSeqs = %s' % json.dumps(jb.ref_seqs(project.sequence_id))
    trackInfo = 'trackInfo = %s' % json.dumps(jb.track_info(all_tracks, assembly_id=project.sequence_id))
    parameters = 'var b = new Browser(%s)' % jb.browser_parameters(
        constants.data_root(), constants.style_root(), constants.image_root(), ','.join([track.name for track in all_tracks]))

    style_control = '''function getFeatureStyle(type, div){
            div.style.backgroundColor='#3333D7';div.className='basic';
            switch(type){
            %s
            }};
            ''' % jb.features_style(all_tracks)


    selections = 'init_locations = %s' % handler.selection.selections(project_id)

    # prepare _gdv_info
    info = {}
    prefix = tg.config.get('prefix')
    if prefix : info['prefix'] = prefix
    info['sequence_id'] = project.sequence_id
    info['admin'] = kw.get('admin', True)
    info['plug_url'] = url('/plugins')
    if kw.has_key('mode'):
        info['mode'] = kw.get('mode')

    info = json.dumps(info)

    control = 'b.showTracks();initGDV(b, %s, %s);' % (project.id, info)

    # add location if it's in url
    if kw.has_key('loc'):
        control += 'b.navigateTo("%s");' % kw.get('loc')

    # prepare jobs list
    jobs = 'init_jobs = %s' % handler.job.jobs(project_id)

    # prepare operation list
    try :
        control_op = 'bs_redirect = %s; bs_operations_path = %s;' % (json.dumps(url('/plugins/index')), json.dumps(plugin.util.get_plugin_path()))
    except Exception as e:
        print "Exception with plugin system : " + str(e)
        control_op = 'init_operations = "connect"'

    return dict(species_name=project.species.name,
        nr_assembly_id=project.sequence_id,
        project_id=project.id,
        is_admin=True,
        ref_seqs = refSeqs,
        track_info = trackInfo,
        parameters = parameters,
        style_control = style_control,
        control = control,
        selections = selections,
        operations_path = control_op,
        jobs = jobs,
        page = 'view')