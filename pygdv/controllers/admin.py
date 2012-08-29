# -*- coding: utf-8 -*-
"""Error controller"""
from tg import request, expose, require
from pygdv.lib.base import BaseController
from pygdv.lib import constants
from pygdv.lib.base import BaseController
from pygdv import model
from repoze.what.predicates import has_any_permission

__all__ = ['AdminController']


class AdminController(BaseController):

    @expose('pygdv.templates.admin')
    @require(has_any_permission('admin', msg='Only for admin'))
    def index(self, *args, **kw):
        return {'page' : 'admin', 'admin_items' : [m.lower() for m in model.admin_models]}
