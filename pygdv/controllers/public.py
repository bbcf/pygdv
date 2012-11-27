from pygdv.lib.base import BaseController
from tg import expose, url, flash
from tg.controllers import redirect
from pygdv.model import DBSession
from pygdv.model import Project

from pygdv import handler

__all__ = ['PublicController']


class PublicController(BaseController):

    @expose('pygdv.templates.view')
    def project(self, id, k, **kw):
        project = DBSession.query(Project).filter(Project.id == id).first()
        if project is None:
            flash('wrong link', 'error')
            raise redirect(url('/home'))
        mode = None

#        if not GenRep().is_up():
#            raise redirect(url('/error', {'m': 'Genrep service is down. Please try again later.'}))

        if k == project.key:
            mode = 'read'
        elif k == project.download_key:
            mode = 'download'

        if mode is None:
            flash('wrong link', 'error')
            raise redirect(url('/home'))

        kw['mode'] = mode
        kw['admin'] = False
        d = handler.view.prepare_view(project.id, **kw)
        return d
