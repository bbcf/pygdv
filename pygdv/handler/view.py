
from pygdv.model import DBSession, Project
from pygdv.lib.jbrowse import util as jb
from pygdv.lib import constants, plugin
import urllib2
import json
import tg
import os
from tg import url


def prepare_view(project_id, *args, **kw):
    from pygdv import handler

    # Get the project
    project = DBSession.query(Project).filter(Project.id == project_id).first()
    tracks = project.success_tracks

    # prepare track that are not yet initialised
    for t in tracks:
        handler.track.init(t)
    DBSession.flush()
    seq = project.sequence
    default_tracks = [d for d in seq.default_tracks if d.status == constants.SUCCESS]
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
    if prefix:
        info['prefix'] = prefix
    info['proxy'] = tg.config.get('main.proxy')
    info['sequence_id'] = project.sequence_id
    info['admin'] = kw.get('admin', True)
    info['plug_url'] = url('/plugins')
    info['project_key'] = project.key
    if 'plugin.service.url' in tg.config:
        info['bioscript_url'] = handler.job.bioscript_url

    if 'mode' in kw:
        info['mode'] = kw.get('mode')

    info = json.dumps(info)

    control = 'b.showTracks();initGDV(b, %s, %s);' % (project.id, info)

    # add location if it's in url
    if 'loc' in kw:
        control += 'b.navigateTo("%s");' % kw.get('loc')

    # prepare jobs list
    jobs = 'init_jobs = %s' % handler.job.jobs(project_id)
    op = '{}'
    if 'plugin.service.url' in tg.config:
        try:
            op = handler.job.operation_list()
        except urllib2.URLError:
            pass
    return dict(species_name=project.species.name,
        nr_assembly_id=project.sequence_id,
        project_id=project.id,
        is_admin=True,
        ref_seqs=refSeqs,
        track_info=trackInfo,
        parameters=parameters,
        style_control=style_control,
        control=control,
        selections=selections,
        jobs=jobs,
        page='view',
        oplist=op)
