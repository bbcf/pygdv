# -*- coding: utf-8 -*-
"""Error controller"""

from tg import request, expose

__all__ = ['HelpController']


class HelpController(object):
    """
    Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.
    
    """
    @expose('pygdv.templates.help')
    def index(self):
        return dict(page='help')
