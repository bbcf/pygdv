# -*- coding: utf-8 -*-
"""Error controller"""

from tg import request, expose
from bbcflib.genrep import GenRep, Assembly

__all__ = ['GenRepController']

chunk = 20000

class GenRepController(object):
  
  
  
  
    @expose()
    def adn(self, ass, chr, id, **kw):
        id = int(id)
        g = GenRep()
        chrs = g.get_genrep_objects('chromosomes', 'chromosome', filters = {'name':chr}, params = {'assembly_id': ass})
        ass = Assembly(ass)
        for chrid, chrs in ass.chromosomes.iteritems():
            if chrs['name'] == chr:
                start = id * chunk
                end = start + chunk
                return g.get_sequence(chrid[0], [[start, end]])
        return ''
        

