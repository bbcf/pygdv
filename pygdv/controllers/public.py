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
import json
from sqlalchemy import and_, not_
__all__ = ['LoginController']



class PublicController(BaseController):
    
    
    
    @expose('pygdv.templates.view')
    def project(self, id, k, **kw):
        project = DBSession.query(Project).filter(and_(Project.id == id, Project.key == k)).first()
        if project is None:
            flash('wrong link', 'error')
            raise redirect('/home')
        print project
        
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
                
                
            DBSession.add(t)
            DBSession.flush()
            trackNames.append(t.name)
        
        refSeqs = 'refSeqs = %s' % json.dumps(jb.ref_seqs(project.sequence_id))
        
        trackInfo = 'trackInfo = %s' % json.dumps(jb.track_info(all_tracks))
        parameters = 'var b = new Browser(%s)' % jb.browser_parameters(
                        constants.data_root(), constants.style_root(), constants.image_root(), ','.join([track.name for track in all_tracks]))
        
        style_control = '''function getFeatureStyle(type, div){
        div.style.backgroundColor='#3333D7';div.className='basic';
        switch(type){
        %s
        }};
        ''' % jb.features_style(all_tracks)
        
        
        
        info = {}
        prefix = tg.config.get('prefix')
        if prefix : info['prefix'] = prefix
        
        control = 'b.showTracks();initGDV(b, %s, %s);' % (project.id, info)
        
        if 'loc' in kw:
            control += 'b.navigateTo("%s");' % kw['loc']
            
        jobs = DBSession.query(Job).filter(and_(Job.project_id == project.id, not_(Job.output == constants.job_output_reload))).all()
        
        jobs_output = [{'job_id' : job.id, 
                       'status' : job.status, 
                       'job_name' : job.name,
                       'job_description' : job.description,
                       'output' : job.output, 
                       'error' : job.traceback}
                      for job in jobs
                      ]
        
        return dict(species_name=project.species.name, 
                    nr_assembly_id=project.sequence_id, 
                    project_id=project.id,
                    is_admin=True,
                    init_jobs=json.dumps(jobs_output),
                    ref_seqs = refSeqs,
                    track_info = trackInfo,
                    parameters = parameters,
                    style_control = style_control,
                    control = control,
                    page='view')
        