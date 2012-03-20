from __future__ import absolute_import

from tg import expose, flash, require, request

from pygdv.lib.base import BaseController
from pygdv.model import DBSession, Project, Track, Sequence
from repoze.what.predicates import has_any_permission
import sqlite3, os
from pygdv.lib import constants
from sqlite3 import OperationalError
import track

class DatabaseController(BaseController):
    

    
    @expose('json')
    def scores(self,  sha1, chr_zoom, imgs, **kw):
        '''
        Get the compurted scores for the database specified, on the chromosome, zoom 
        and for the images specified. It works with the ``signal`` database.
        @param sha1 : the sha1 of the database
        @param chr : the chromosome
        @param zoom : the zoom
        @param imgs : the list of images needed
        @return a json : {name : {image_nb : {image_data}}. With image_data = [pos, score, pos, score, ...]
        '''
        
        
        name = '%s/%s' % (sha1, chr_zoom)
        
        conn = sqlite3.connect(os.path.join(constants.json_directory(), sha1, chr_zoom))

        data = {}
        db_data = {}
        
        for im in imgs.split(',') :
                
            im_data = []
            cur = conn.cursor()
            try :
                cur.execute('select pos, score from sc where number = ? order by pos asc;', (im,))
            except OperationalError as e:
                return '{}'
            
            r = False
            for row in cur : 
                r = True
                im_data += [row [0], round(row[1], 3)]
            
            #print 'for image %s : %s' %(im, im_data)
            # if no result from previous query, put score from an image before
#            if not r :
#                cur.execute('select score from sc where number < ? order by number desc limit 1;', (im,))
#                row = cur.fetchone()
#                if row:
#                    im_data += [0, row[0]]
                
            db_data[im] = im_data
            cur.close()
        conn.close()
        data[name]=db_data
        return data
            
            
    @expose('json')
    def search(self, project_id, term, *args, **kw):
        project = DBSession.query(Project).filter(Project.id == project_id).first()
        sequence = project.sequence
        default = sequence.default_tracks
        if default is None or len(default) < 1:
            return {}
        t = default[0]
        chrs = {}
        with track.load(t.path, 'sql', readonly=True) as t:
            gene_name_alias =  t.find_column_name(['name', 'gene_name', 'gene name', 'gname', 'Name', 'product'])
            try :
                for row in t.search({gene_name_alias : term}, [gene_name_alias, 'start', 'end']):
                    chr, name, start, stop = row
                    if chr not in chrs:
                        chrs[chr] = {}
                        
                    names = chrs[chr]
                    if name in names:
                        old = names[name]
                        start = min(old[0], start)
                        stop = max(old[1], stop)
                    names[name] = [start, stop] 
            except Exception as e:
                return {} 
                
        
        #result[chr].append([name, start, stop])
        result = {}
        for chr, names in chrs.iteritems() :
            result[chr] = []
            for k, v in names.iteritems():
                result[chr].append([k, v[0], v[1]])
        
        return result
    
