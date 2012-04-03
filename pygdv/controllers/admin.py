# -*- coding: utf-8 -*-
"""Error controller"""
from tg import request, expose
from pygdv.lib.base import BaseController
from pygdv.lib import constants
from pygdv.lib.base import BaseController
from pygdv import model
from repoze.what.predicates import has_permission

__all__ = ['AdminController']


class AdminController(BaseController):
    allow_only = has_permission(constants.perm_admin)

    @expose('pygdv.templates.admin')
    def index(self, *args, **kw):
        return {'page' : 'admin', 'admin_items' : [m.lower() for m in model.admin_models]}
