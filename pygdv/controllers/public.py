from pygdv.lib.base import BaseController
from pygdv.lib import tequila, constants
from tg import expose,url,flash,request,response
from tg.controllers import redirect
from pygdv.model import User, Group, DBSession
from pygdv.config.app_cfg import token
import transaction
import datetime
from tg import app_globals as gl
import tg
from pygdv.model import DBSession, Project, Job
from pygdv.lib.jbrowse import util as jb
from pygdv.lib import constants, reply
from pygdv.celery import tasks
import json
from sqlalchemy import and_, not_

from pygdv import handler

__all__ = ['LoginController']



class PublicController(BaseController):
    
    @expose()
    def test(self, *args, **kw):
        t = tasks.test_command_line.delay(*args, **kw)
        return dict(task_id=t.task_id)
    
    @expose('pygdv.templates.view')
    def project(self, id, k, **kw):
        project = DBSession.query(Project).filter(Project.id == id).first()
        if project is None:
            flash('wrong link', 'error')
            raise redirect(url('/home'))
        mode = None
        
#        if not GenRep().is_up():
#            raise redirect(url('/error', {'m': 'Genrep service is down. Please try again later.'}))
        
        
        if k == project.key : mode = 'read'
        elif k == project.download_key : mode = 'download'
        
        if mode is None :
            flash('wrong link', 'error')
            raise redirect(url('/home'))
        
        
        tracks = project.tracks
        
        seq = project.sequence
        default_tracks = seq.default_tracks
        all_tracks = tracks + default_tracks
        
        trackNames = []
        for t in all_tracks:
            while t.name in trackNames:
                ind = 0
                while(t.name[-(ind + 1)].isdigit()):
                    ind += 1
                cpt = t.name[-ind:]
                try : 
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
        
        refSeqs = 'refSeqs = %s' % json.dumps(jb.ref_seqs(project.sequence_id))
        
        trackInfo = 'trackInfo = %s' % json.dumps(jb.track_info(all_tracks, assembly_id=project.sequence_id))
        parameters = 'var b = new Browser(%s)' % jb.browser_parameters(
                        constants.data_root(), constants.style_root(), constants.image_root(), ','.join([track.name for track in all_tracks]))
        
        selections = 'init_locations = %s' % handler.selection.selections(id)

        style_control = '''function getFeatureStyle(type, div){
        div.style.backgroundColor='#3333D7';div.className='basic';
        switch(type){
        %s
        }};
        ''' % jb.features_style(all_tracks)
        
        
        
        info = {}
        prefix = tg.config.get('prefix')
        info['admin'] = False
        info['mode'] = mode
        info['sequence_id'] = project.sequence_id
        if prefix : info['prefix'] = prefix
        info = json.dumps(info)
        control = 'b.showTracks();initGDV(b, %s, %s);' % (project.id, info)
        
        if 'loc' in kw:
            control += 'b.navigateTo("%s");' % kw['loc']
            
        jobs = 'init_jobs = %s' % handler.job.jobs(id)
        
        
        return dict(species_name=project.species.name, 
                    nr_assembly_id=project.sequence_id, 
                    project_id=project.id,
                    is_admin=False,
                    ref_seqs = refSeqs,
                    track_info = trackInfo,
                    parameters = parameters,
                    style_control = style_control,
                    control = control,
                    selections = selections,
                    jobs = jobs,
                    page='view')
        
        
        
        
        
      
            