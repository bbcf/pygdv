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
from pygdv.widgets import datagrid, form
from pygdv import handler
from pygdv.lib import util, constants, checker, reply
from pygdv.worker import tasks
import tempfile, track
import tw2.core as twc
import json
__all__ = ['TrackController']






class TrackController(BaseController):
    allow_only = has_any_permission(constants.perm_user, constants.perm_admin)
    
    
    

    @expose('pygdv.templates.track_index')
    @expose('json')
    #@paginate('items', items_per_page=10)
    @with_trailing_slash
    def index(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        shared_by = None
        # view on a specific project
        if kw.has_key('pid'):
            project_id = kw.get('pid')
            project = DBSession.query(Project).filter(Project.id == project_id).first()
            if project is None:
                flash("Project doesn't exists", "error")
                raise redirect('/tracks')
            if not checker.check_permission(user=user, project=project, right_id=constants.right_read_id) and not checker.is_admin(user=user):
                flash('You must have %s permission to view the project.' % constants.right_read, 'error')
                raise redirect('/tracks')
            tracks = project.tracks
            # view on user project
            if checker.own(user=user, project=project):
                kw['own'] = True
                kw['upload'] = True
                grid = datagrid.track_grid

            # view from a shared user
            else :
                rights = handler.project.get_rights(project=project, user=user)
                if constants.right_upload_id in [r.id for r in rights]:
                    kw['upload'] = True
                grid = datagrid.track_grid_permissions(user=user, rights=rights)
                shared_by = "%s %s" % (project.user.firstname, project.user.name[0].upper())
            kw['pn'] = project.name
            track_list = [util.to_datagrid(grid, tracks, "Track Listing", len(tracks)>0)]
            shared_with = project.get_circle_with_right_display

        # view all user tracks
        else :
            shared_with = ''
            tracks = user.tracks
            track_list = [util.to_datagrid(datagrid.track_grid, tracks, "Track Listing", len(tracks)>0)]
            kw['upload'] = True

        t = handler.help.help_address(url('/help'), 'main', 'track list help')

        # project list
        project_list = [(p.id, p.name,) for p in user.projects]

        # shared projects
        shared_with_rights = handler.project.get_shared_projects(user)
        sorted_projects = sorted(shared_with_rights.iteritems(), key=lambda k : k[0].name)
        shared_project_list = [(p.id, p.name, ''.join([r[0] for r in rights])) for p, rights in sorted_projects]

        return dict(page='tracks', model='track', form_title="new track", track_list=track_list,
            project_list=project_list, shared_project_list=shared_project_list, value=kw,
            tooltip=t, project_id=kw.get('pid', None), upload=kw.get('upload', None), project_name=kw.get('pn', None),
            shared_with=shared_with, owner=kw.get('own', False), shared= not kw.get('own', False), shared_by=shared_by)



    @require(not_anonymous())
    @with_trailing_slash
    @expose('pygdv.templates.track_new')
    def new(self, *args, **kw):

        project_name = None
        ass_name = None
        project_id = None
        value = {}
        if kw.has_key('pid'):
            new_form = form.NewTrackPrefilled(action=url('/tracks/create')).req()
            project_id = kw.get('pid')
            project = DBSession.query(Project).filter(Project.id == project_id).first()
            project_name = project.name
            ass_name = project.sequence.name
            value['project_id'] = project_id
        else:
            new_form = form.NewTrack(action=url('/tracks/create')).req()
            species = DBSession.query(Species).all()
            sp_opts =  [(sp.id,sp.name) for sp in species]
            new_form.child.children[3].options = sp_opts
            mapping = json.dumps(dict([(sp.id, [(seq.id, seq.name) for seq in sp.sequences]) for sp in species]))
            value['smapping'] = mapping

        new_form.value = value
        return dict(page='tracks', widget=new_form, project_id=project_id, project_name=project_name, ass_name=ass_name)

    @expose('json')
    def create(self, *args, **kw):
        user = handler.user.get_user_in_session(request)
        # change a parameter name
        if kw.has_key('assembly'):
            kw['sequence_id'] = kw.get('assembly')
            del kw['assembly']
        if kw.has_key('urls'):
            kw['url']=kw.get('urls')
            del kw['urls']
        for k, v in kw.iteritems():
            if v == 'None': kw[k] = None

        project_id = kw.get('project_id', '')
        if project_id == '' : project_id = None
        # verify track parameters
        try :
            handler.track.pre_track_creation(url=kw.get('url', None),
                file_upload=kw.get('file_upload', None),
                fsys=kw.get('fsys', None),
                project_id=project_id,
                sequence_id=kw.get('sequence_id', None))
        except Exception as e:
            print 'Bad params : %s' %e
            if project_id is not None:
                reply.error(request, str(e), tg.url('./new', {'pid' : project_id}), {})
            return reply.error(request, str(e), tg.url('./new'), {})

        # get parameters
        track_name, extension, sequence_id = handler.track.fetch_track_parameters(
            url=kw.get('url', None),
            file_upload=kw.get('file_upload', None),
            fsys=kw.get('fsys', None),
            trackname=kw.get('trackname', None),
            extension=kw.get('extension', None),
            project_id=project_id,
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
        if util.is_compressed(extension) or (kw.get('url', None)!=None and len(kw.get('url', '').split())>1):
            async = tasks.multiple_track_input.delay(kw.get('uploaded', None), kw.get('file', None), kw.get('url', None), kw.get('fsys', None),
                sequence_id, user.email, user.key, project_id, kw.get('force', False), kw.get('delfile', False),
                constants.callback_track_url(), extension)
            return reply.normal(request, 'Processing launched.', '/tracks/', {'task_id' : async.task_id})
        else :
            # create a new track
            _track = handler.track.new_track(user.id, track_name, sequence_id=sequence_id, admin=False, project_id=project_id)

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

            if project_id is not None:
                return reply.normal(request,'Processing launched.', tg.url('/tracks/', {'pid' : project_id}), {'task_id' : async.task_id,
                                                                                                                  'track_id' : _track.id})
            return reply.normal(request, 'Processing launched.', '/tracks/', {'task_id' : async.task_id,
                                                                        'track_id' : _track.id})

    @expose('json')
    def post(self, *args, **kw):
        print 'post %s' % kw
        project_id = kw.get('project_id', None)
        urls = kw.get('urls', None)
        fu = kw.get('file_upload', None)

        if (fu is None or fu == '') and (urls is None or urls == ''):
            flash('Missing field', 'error')
            raise redirect('/tracks/new')

        print 'before create'
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

    @expose('json')
    def delete(self, track_id, **kw):
        user = handler.user.get_user_in_session(request)
        if track_id is not None:
            if not checker.can_edit_track(user, track_id) :
                return reply.error(request, "You haven't the right to delete any tracks which is not yours", '/tracks', {'error' : 'wrong credential'})
            handler.track.delete_track(track_id=track_id)
        return reply.normal(request, 'Track successfully deleted.', '/tracks', {'success' : 'track deleted'})

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
        if not checker.can_download_track(user.id, track_id) and not checker.user_is_admin(user.id):
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
        response.headerlist.append(('Content-Disposition', 'attachment;filename=%s.sqlite' % track.name))
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
    @expose('pygdv.templates.track_admin')
    @expose('json')
    #@paginate('items', items_per_page=10)
    @with_trailing_slash
    def admin(self, **kw):
        # view on a specific project
        grid = datagrid.track_admin_grid
        if kw.has_key('pid'):
            project_id = kw.get('pid')
            project = DBSession.query(Project).filter(Project.id == project_id).first()
            tracks = project.tracks
            kw['upload'] = True

            kw['pn'] = project.name
            track_list = [util.to_datagrid(grid, tracks, "Track Listing", len(tracks)>0)]

        else :
            if 'user_id' in kw:
                tracks = DBSession.query(Track).filter(Track.user_id == kw['user_id']).all()
            else :
                tracks = DBSession.query(Track).all()
            track_list = [util.to_datagrid(grid, tracks, "Track Listing", len(tracks)>0)]
            kw['upload'] = True

        # track list

        t = handler.help.tooltip['admin']

        # project list
        all_projects = DBSession.query(Project).all()
        project_list = [(p.id, p.name,) for p in all_projects]


        return dict(page='tracks', model='track', form_title="new track", track_list=track_list,
            project_list=project_list, shared_project_list=[], value=kw,
            tooltip=t, project_id=kw.get('pid', None), upload=kw.get('upload', None), project_name=kw.get('pn', None))






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
