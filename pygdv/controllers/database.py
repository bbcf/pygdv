from __future__ import absolute_import

from tg import expose, flash, require, request

from pygdv.lib.base import BaseController
from pygdv.model import DBSession, Project, Track, Sequence
from repoze.what.predicates import has_any_permission
from tg import app_globals as gl
import sqlite3, os
from pygdv.lib import constants
from sqlite3 import OperationalError
import track

class DatabaseController(BaseController):
    allow_only = has_any_permission(gl.perm_user, gl.perm_admin)

    
    @expose('json')
    def scores(self,  sha1, chr_zoom, imgs, **kw):
        '''
        Get the compurted scores for the database specified, on the chromosome, zoom 
        and for the images specified. It works with the ``signal`` database.
        @param sha1 : the sha1 of the database
        @param chr : the chromosome
        @param zoom : the zoom
        @param imgs : the list of images needed
        @return a json : {name : {image_nb : {immage_data}}
        '''
        name = '%s/%s' % (sha1, chr_zoom)
        
        conn = sqlite3.connect(os.path.join(constants.json_directory(), sha1, chr_zoom))

        data = {}
        db_data = {}
        
        for im in imgs.split(',') :
            im_data = {}
            cur = conn.cursor()
            try :
                cur.execute('select pos, score from sc where number = ? order by pos asc;', (im,))
            except OperationalError as e:
                return '{}'
            
            r = False
            for row in cur : 
                r = True
                im_data[row[0]]=row[1]
            # if no result from previous query, put score from an image before
            if not r :
                cur.execute('select score from sc where number < ? order by number desc limit 1;', (im,))
                row = cur.fetchone()
                im_data[0]=row[0]
                
            db_data[im] = im_data
            cur.close()
        conn.close()
        data[name]=db_data
        return data
            
            
    @expose('json')
    def search(self, project_id, term, *args, **kw):
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        sequence = project.sequence
        t = sequence.default_tracks[0]
        with track.load(t.path, 'sql', readonly=True) as t:
            data = [row for row in t.search({'gene_name' : term})]
        return data
    
