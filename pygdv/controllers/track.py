"""Track Controller"""
from __future__ import absolute_import

from pygdv.lib.base import BaseController
from tgext.crud import CrudRestController


from repoze.what.predicates import not_anonymous, has_any_permission, has_permission
import tg, sys, traceback
from tg import expose, flash, require, tmpl_context, validate, request, response, url
from tg.controllers import redirect
from tg.decorators import with_trailing_slash

from pygdv.model import DBSession, Track, Sequence, Input, Task, Project, Species
from pygdv.widgets.track import track_table, track_export, track_table_filler, track_new_form, track_new_form2, OneMissingSchema, track_edit_form, track_grid, default_track_form
from pygdv.widgets import datagrid, form
from pygdv import handler
from pygdv.lib import util, constants, checker, reply
from pygdv.celery import tasks
import tempfile, track
import tw2.core as twc
__all__ = ['TrackController']






class TrackController(BaseController):
    allow_only = has_any_permission(constants.perm_user, constants.perm_admin)
    
    
    

    @expose('pygdv.templates.track_index')
    @expose('json')
    #@paginate('items', items_per_page=10)
    @with_trailing_slash
    def index(self, *args, **kw):
        user = handler.user.get_user_in_session(request)

        # view on a specific project
        if kw.has_key('pid'):
            project_id = kw.get('pid')
            project = DBSession.query(Project).filter(Project.id == project_id).first()
            if not checker.check_permission(user=user, project=project, right_id=constants.right_read_id):
                flash('You must have %s permission to view the project.' % constants.right_read, 'error')
                raise redirect('/tracks')
            tracks = project.tracks
            if checker.own(user=user, project=project):
                kw['upload'] = True
                grid = datagrid.track_grid
            else :
                rights = handler.project.get_rights(project=project, user=user)

                if constants.right_upload_id in [r.id for r in rights]:
                    kw['upload'] = True
                grid = datagrid.track_grid_permissions(rights=rights)
            kw['pn'] = project.name
            track_list = [util.to_datagrid(grid, tracks, "Track Listing", len(tracks)>0)]

        else :
            tracks = user.tracks
            track_list = [util.to_datagrid(datagrid.track_grid, tracks, "Track Listing", len(tracks)>0)]
            kw['upload'] = True

        # track list

        t = handler.help.tooltip['main']
        
        # project list
        project_list = [(p.id, p.name,) for p in user.projects]

        # shared projects
        shared_with_rights = handler.project.get_shared_projects(user)
        sorted_projects = sorted(shared_with_rights.iteritems(), key=lambda k : k[0].name)
        shared_project_list = [(p.id, p.name, ''.join([r[0] for r in rights])) for p, rights in sorted_projects]

        return dict(page='tracks', model='track', form_title="new track", track_list=track_list,
            project_list=project_list, shared_project_list=shared_project_list, value=kw,
            tooltip=t, project_id=kw.get('pid', None), upload=kw.get('upload', None), project_name=kw.get('pn', None))



    @require(not_anonymous())
    @with_trailing_slash
    @expose('pygdv.templates.track_new')
    def new(self, *args, **kw):

        if kw.has_key('pid'):
            project_id = kw.get('pid')
            project = DBSession.query(Project).filter(Project.id == project_id).first()
            project_name = project.name
            ass_name=project.sequence.name
            tmpl_context.widget = track_new_form2
            kw['project_id']=project_id
            del kw['pid']
        else:
            project_name=None
            ass_name=None
            project_id=None
            tmpl_context.widget = track_new_form
        
        return dict(page='tracks', value=kw, model='track', project_id=project_id, project_name=project_name, ass_name=ass_name)

    @expose('json')
    def create(self, *args, **kw):
        print 'create %s ' % kw
        user = handler.user.get_user_in_session(request)
        # change a parameter name
        if kw.has_key('assembly'):
            kw['sequence_id'] = kw.get('assembly')
            del kw['assembly']
        if kw.has_key('urls'):
            kw['url']=kw.get('urls')
            del kw['urls']



        # verify track parameters
        try :
            handler.track.pre_track_creation(url=kw.get('url', None),
                file_upload=kw.get('file_upload', None),
                fsys=kw.get('fsys', None),
                project_id=kw.get('project_id', None),
                sequence_id=kw.get('sequence_id', None))
        except Exception as e:
            if kw.has_key('project_id'):
                reply.error(request, str(e), tg.url('./new', {'pid' : kw.get('project_id')}), {})
            return reply.error(request, str(e), tg.url('./new'), {})

        # get parameters
        track_name, extension, sequence_id = handler.track.fetch_track_parameters(
            url=kw.get('url', None),
            file_upload=kw.get('file_upload', None),
            fsys=kw.get('fsys', None),
            trackname=kw.get('trackname', None),
            extension=kw.get('extension', None),
            project_id=kw.get('project_id', None),
            sequence_id=kw.get('sequence_id', None))

        # upload the track it's from file_upload
        if request.environ[constants.REQUEST_TYPE] == constants.REQUEST_TYPE_BROWSER :
            fu = kw.get('file_upload', None)
            if fu is not None:
                kw['uploaded']=True
                _f = util.download(file_upload=fu,
                    filename=track_name, extension=extension)
                kw['file']=_f.name
                del kw['file_upload']

        # check if multiples url or if zipped file
        multiple = False
        if kw.get('uploaded', False):
            if util.is_compressed(kw.get('file')):
                multiple = True
        else:
            _urls = kw.get('url', '')
            if len(_urls.split()) > 1 or util.is_compressed(_urls, is_url=True):
                multiple = True
        if multiple:
            async = tasks.multiple_track_input.delay(kw.get('uploaded', None), kw.get('file', None), kw.get('url', None), kw.get('fsys', None),
                sequence_id, user.email, user.key, kw.get('project_id', None), kw.get('force', False), kw.get('delfile', False), constants.callback_track_url(),
            )
            return reply.normal(request, 'Processing launched.', './', {'task_id' : async.task_id})



        else :
            # create a new track
            _track = handler.track.new_track(user.id, track_name, sequence_id=sequence_id, admin=False, project_id=kw.get('project_id', None))

            # format parameters
            _uploaded = kw.get('uploaded', False)
            _file = kw.get('file', None)
            _urls = kw.get('url', None)
            _fsys=kw.get('fsys', None)
            _track_name = track_name
            _extension = extension
            _callback_url = constants.callback_track_url()
            _force = kw.get('force', False)
            _delfile = kw.get('delfile', False)
            _track_id = _track.id
            _user_key = user.key
            _user_mail = user.email

            # launch task with the parameters
            async = tasks.track_input.delay(_uploaded, _file, _urls, _fsys, _track_name, _extension, _callback_url, _force,
                _track_id, _user_mail, _user_key, sequence_id, _delfile)

            # update the track
            handler.track.update(track=_track, params={'task_id' : async.task_id})

            if kw.has_key('project_id'):
                return reply.normal(request,'Processing launched', tg.url('./', {'pid' : kw.get('project_id')}), {'task_id' : async.task_id,
                                                                                                                  'track_id' : _track.id})
            return reply.normal(request, 'Processing launched.', './', {'task_id' : async.task_id,
                                                                        'track_id' : _track.id})

    @expose('json')
    @validate(track_new_form, error_handler=new)
    def post(self, *args, **kw):
        project_id = kw.get('project_id', None)
        urls = kw.get('urls', None)
        fu = kw.get('file_upload', None)

        if (fu is None or fu == '') and (urls is None or urls == ''):
            flash('Missing field', 'error')
            raise redirect('/tracks/new')
        print 'posted'
        return self.create(*args, **kw)
    
    @expose('json')
    def post2(self, *args, **kw):
        project_id = kw.get('project_id', None)
        urls = kw.get('urls', None)
        fu = kw.get('file_upload', None)
        if (fu is None or fu == '') and (urls is None or urls == ''):
            flash('Missing field', 'error')
            raise redirect('/tracks/new', {'pid' : project_id})
        print 'posted2'
        return self.create(*args, **kw)

    #@expose('genshi:tgext.crud.templates.post_delete')
    @expose()
    def delete(self, track_id, **kw):
        user = handler.user.get_user_in_session(request)
        if track_id is not None:
            if not checker.can_edit_track(user, track_id) :
                flash("You haven't the right to edit any tracks which is not yours", 'error')
                raise redirect('../')
            handler.track.delete_track(track_id=track_id)
        raise redirect('../')

    @with_trailing_slash
    @expose('pygdv.templates.track_edit')
    def edit(self, track_id, **kw):
        user = handler.user.get_user_in_session(request)
        if track_id is not None:
            if not checker.can_edit_track(user, track_id) :
                flash("You haven't the right to edit any tracks which is not yours", 'error')
                raise redirect('/tracks')

        widget = form.EditTrack(action=url('/tracks/edit/%s' % track_id)).req()

        track = DBSession.query(Track).filter(Track.id == track_id).first()

        d = {}
        d['name'] = track.name
        if track.parameters is None:
            cc = constants.default_track_color
        else :
            cc = track.parameters.color
        d['track_id'] = track_id
        d['color'] = cc
        widget.value = d
        if request.method == 'GET':
            return dict(title='Edit track', page='track', widget=widget, color=cc )

        if request.method == 'POST':
            try:
                widget.validate(kw)
            except twc.ValidationError as e:
                return dict(title='Edit track', page='track', widget=e.widget, color=cc)

        handler.track.edit(track=track, name=kw.get('name', None), color=kw.get('color', None))
        raise redirect('/tracks')

    @expose()
    @validate(track_edit_form, error_handler=edit)
    def put(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        _id = args[0]

        if not checker.can_edit_track(user, _id) and not checker.user_is_admin(user.id):
            flash("You haven't the right to edit any tracks which is not yours")
            raise redirect('../')

        track = DBSession.query(Track).filter(Track.id == _id).first()
        track.name = kw['name']
        if 'color' in kw:
            track.parameters.color = kw.get('color')
        DBSession.flush()
        redirect('../')



    @expose('pygdv.templates.track_export')
    def export(self, track_id, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.can_download_track(user.id, track_id)  and not checker.user_is_admin(user.id):
            flash("You haven't the right to export any tracks which is not yours")
            raise redirect('../')
        track = DBSession.query(Track).filter(Track.id == track_id).first()

        data = util.to_datagrid(track_grid, [track])
        tmpl_context.form = track_export
        kw['track_id']=track_id
        return dict(page='tracks', model='Track', info=data, form_title='', value=kw)

    @expose()
    def dump(self, track_id, format,  *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.can_download_track(user.id, track_id)  and not checker.user_is_admin(user.id):
            flash("You haven't the right to export any tracks which is not yours", 'error')
            raise redirect('../')
        _track = DBSession.query(Track).filter(Track.id == track_id).first()
        if format == 'sqlite':
            response.content_type = 'application/x-sqlite3'
            return open(_track.path).read()
        else :
            tmp_file = tempfile.NamedTemporaryFile(delete=True)
            tmp_file.close()
            track.convert(_track.path, (tmp_file.name, format))
            response.content_type = 'text/plain'
            return open(tmp_file.name).read()

    @expose()
    def link(self, track_id, *args, **kw):
        user = handler.user.get_user_in_session(request)
        if not checker.user_own_track(user.id, track_id)  and not checker.user_is_admin(user.id):
            flash("You haven't the right to download any tracks which is not yours", 'error')
            raise redirect('/tracks/')
        track = DBSession.query(Track).filter(Track.id == track_id).first()
        if track.status == constants.ERROR:
            flash("The track processing failed. You cannot download it.", 'error')
            raise redirect('/tracks/')
        response.content_type = 'application/x-sqlite3'
        return open(track.path).read()



    @expose()
    def traceback(self, track_id):
        user = handler.user.get_user_in_session(request)

        if not checker.user_own_track(user.id, track_id) and not checker.user_is_admin(user.id):

            flash("You haven't the right to look at any tracks which is not yours", 'error')
            raise redirect('/tracks')
        track = DBSession.query(Track).filter(Track.id == track_id).first()
        return track.traceback

    @expose()
    def copy(self, track_id):
        user = handler.user.get_user_in_session(request)
        if not checker.can_download_track(user.id, track_id):
            return reply.error(request, 'You have no right to copy this track in your profile.', './', {})
        t = DBSession.query(Track).filter(Track.id == track_id).first()
        if not t:
            return reply.error(request, 'No track with this id.', './', {})
        handler.track.copy_track(user.id, t)
        return reply.normal(request, 'Copy successfull', './', {})




    ##### for ADMINS #######




    @require(has_permission('admin', msg='Only for admins'))
    @expose('pygdv.templates.form')
    def default_tracks(self, **kw):
        tmpl_context.widget = default_track_form
        return dict(page='tracks', value=kw, title='new default track (visible on all projects with the same assembly)')

    @expose()
    @require(has_permission('admin', msg='Only for admins'))
    @validate(default_track_form, error_handler=default_tracks)
    def default_tracks_upload(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        kw['admin'] = True
        util.file_upload_converter(kw)

        task_id = tasks.process_track.delay(user.id, **kw)
        return reply.normal(request, 'Task launched.', '/home', {'task_id' : task_id})

    @require(has_permission('admin', msg='Only for admins'))
    @expose('pygdv.templates.list')
    def admin(self, **kw):
        sequences = DBSession.query(Sequence).all()
        tracks = []
        for sequence in sequences:
            tracks += sequence.default_tracks
        data = [util.to_datagrid(track_grid, tracks, "Track Listing", len(tracks)>0)]
        t = handler.help.tooltip['track']
        return dict(page='tracks', model='track', tooltip=t, form_title="admin tracks",items=data,value=kw)

    @require(has_permission('admin', msg='Only for admins'))
    @expose('pygdv.templates.list')
    def all(self, *args, **kw):
        if 'user_id' in kw:
            tracks = DBSession.query(Track).filter(Track.user_id == kw['user_id']).all()
        else :
            tracks = DBSession.query(Track).all()
        t = handler.help.tooltip['track']
        data = [util.to_datagrid(track_grid, tracks, "Track Listing", len(tracks)>0)]
        return dict(page='tracks', model='track', tooltip=t, form_title="new track",items=data,value=kw)






    @expose('json')
    def after_sha1(self, fname, sha1, force, callback_url, track_id, old_task_id, mail, key, sequence_id, extension, trackname):
        """
        Called after a sha1 where calculated on a file.
        If the sha1 already exist, only the databases operations are done.
        Else the input will go in the second part of the process.
        The input can be 'forced' to be recomputed
        """
        try :
            _input = DBSession.query(Input).filter(Input.sha1 == sha1).first()
            do_process = True
            if util.str2bool(force) and _input is not None :
                handler.track.delete_input(_input.sha1)
                DBSession.delete(_input)
                DBSession.flush()
            elif _input is not None:
                do_process = False
                handler.track.update(track_id=track_id,
                    params={'new_input_id' : _input.id})
                handler.track.finalize_track_creation(track_id=track_id)

            if do_process :

                handler.track.update(track_id=track_id, params={'sha1' : sha1})
                sequence = DBSession.query(Sequence).filter(Sequence.id == sequence_id).first()
                async = tasks.track_process.delay(mail, key, old_task_id, fname, sha1, callback_url, track_id, sequence.name, extension, trackname, callback_url)

                handler.track.update(track_id=track_id,
                    params={'new_task_id' : async.task_id})
            return {'success' : 'to second process'}
        except Exception as e:
            etype, value, tb = sys.exc_info()
            traceback.print_exception(etype, value, tb)


            return {'error' : str(e)}


    @expose('json')
    def after_process(self, mail, key, old_task_id, track_id, datatype):
        print '[x] after process [x] %s' % track_id
        task = DBSession.query(Task).filter(Task.task_id == old_task_id).first()
        if task is not None :
            DBSession.delete(task)
            DBSession.flush()
        if not track_id == 'None':
            handler.track.update(track_id=track_id, params={'datatype' : datatype})
            handler.track.finalize_track_creation(track_id=track_id)
        return {'success' : 'end'}
