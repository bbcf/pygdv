# -*- coding: utf-8 -*-
"""Error controller"""

from tg import request, expose
from pygdv import handler

__all__ = ['HelpController']


class HelpController(object):
    """
    """
    @expose('pygdv.templates.help')
    def index(self):
        return dict(page='help')


