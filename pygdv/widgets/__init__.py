# -*- coding: utf-8 -*-
"""The widget package contains all widgets (tables, form, ... needed for the project)"""
from pygdv.lib import constants
from tw.forms.datagrid import Column
from tg import request, url
from sqlalchemy import asc, desc
import genshi, re, urllib2



class ModelWithRight(object):
    '''
    Generic class to dynamically add right of viewing on a model object.
    '''
    
    def __init__(self, obj, rights):
        self.dec = obj
        self.rights = rights






class SortableColumn(Column):
    def __init__(self, title, name):
        super(SortableColumn, self).__init__(name)
        self._title = title
        
        
    def set_title(self, title):
        self._title = title
        
    def get_title(self):
        cur_ordering = request.GET.get('ordercol')
        if cur_ordering is not None:
            cur_ordering = urllib2.unquote(cur_ordering.encode('utf8'))
            args = re.findall('(\+|\-){1}(\w+)+', cur_ordering)
            isin = False
            
            for i in range(len(args)):
                tmp = args[i]
                sign = tmp[0]
                word = tmp[1]
                
                if word == self.name:
                    sign = sign == '+' and '-' or '+'
                    isin = True
                    args[i] = (sign, word)
                    
            if not isin:
                args.append(('+', self.name))
                
        else :
            args = [('+', self.name)]
        new_params = dict(request.GET)
        new_params['ordercol'] = ''.join('%s%s' % (k, v) for k, v in args)
        
        new_url = url(request.path_url, params=new_params)
        return genshi.Markup('<a href=%s > %s </a>' % (new_url, self._title))
        
    title = property(get_title, set_title)
        