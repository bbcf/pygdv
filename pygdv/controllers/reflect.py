from __future__ import absolute_import

from tg import expose, flash, require, request

from pygdv.lib.base import BaseController
from pygdv.model import DBSession, Project, Track, Sequence
from repoze.what.predicates import has_any_permission
import sqlite3, os
from pygdv.lib import constants
from sqlite3 import OperationalError
import track, urllib2, urllib



reflect_server = 'http://reflect.ws'

reflect_api = 'REST'

reflect_popup = 'GetPopup'

class ReflectController(BaseController):
    allow_only = has_any_permission(constants.perm_admin, constants.perm_user)


    @expose()
    def links(self, name, assembly_id):
        print 'links'
        url = '%s/%s/%s?name=%s' % (reflect_server, reflect_api, reflect_popup, name)
        print url
        u = urllib2.urlopen(url)
        print u
        return u