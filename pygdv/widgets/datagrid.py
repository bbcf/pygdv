from pygdv.lib import constants, helpers
import tw.forms as twf
import genshi
from tg import url

DEBUG_LEVEL = 0


def debug(s, t=0):
    if DEBUG_LEVEL > 0:
        print '[datagrid] %s%s' % ('\t' * t, s)

hidden_info = genshi.Markup("<span class='table_hidden'>hidden_info</span>")

hoover_action = genshi.Markup("<div class='table_hidden'>hidden_info</div>")


def hoover_actions(actions):
    return genshi.Markup("<div class='hoover_actions table_hidden'>%s</div>" % actions)


def hide_info(dict):
    span = ''
    for k, v in dict.iteritems():
        span += "<span class='table_hidden %s'>%s</span>" % (k, v)
    return genshi.Markup("<div class='hidden_info'>%s</div>" % span)

sequences_grid = twf.DataGrid(fields=[
    ('ID', 'id'),
    (hoover_action, lambda obj: hoover_actions(
        helpers.edit_link(obj.id, url('/sequences'))
    )),
    ('SPECIES', 'species.name'),
    ('NAME', 'name'),
    ('TRACKS', lambda obj: ', '.join(['%s' % (t.name) for t in obj.default_tracks])),
    ('PUBLIC', 'public'),
    ('USERS', lambda obj: ', '.join(['%s' % (u.email) for u in obj.users]))

])
"""
 #column
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    description = Column(Text(), nullable=False)

    _created = Column(DateTime, nullable=False, default=datetime.now)
    user_id = Column(Integer, ForeignKey('User.id', ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey('Project.id', ondelete="CASCADE"), nullable=True)
    status = Column(Unicode(255))
    ext_task_id = Column(VARCHAR(255), unique=True)
    bioscript_url = Column(VARCHAR(255))
    traceback = Column(Text, nullable=True)
"""

job_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    (hoover_action, lambda obj: hoover_actions(
        helpers.delete_link(obj.id, url('/jobs'))
    )),
    ('Project', 'project.name'),
    ('Bioscript', lambda x: genshi.Markup(helpers.bioscript(x.bioscript_url))),
    ('Traceback', lambda x: genshi.Markup('''<a href="%s">traceback</a>''' % url('/jobs/traceback?id=%s' % x.id))),
    ('Created', 'created'),
    (hidden_info, lambda obj: hide_info({
        'tr_status': obj.status,
        'tr_info': obj.traceback
    }))
])


def get_actions(track, user, rights, project=None):
    # user own the track => all actions
    if track.user.id == user.id:
        return hoover_actions(
            helpers.export_link(track.id, url('/tracks'), project=project)
            + helpers.edit_link(track.id, url('/tracks'), project=project)
            + helpers.delete_link(track.id, url('/tracks'), project=project)
        )
    right_ids = [r.id for r in rights]
    if rights is None:
        return hoover_actions('')
    debug('Get actions %s' % right_ids)
    if constants.rights['download']['id'] in right_ids and constants.rights['upload']['id'] in right_ids:
        debug('Download & Upload', 1)
        return hoover_actions(
            helpers.export_link(track.id, url('/tracks'), project=project)
            + helpers.edit_link(track.id, url('/tracks'), project=project)
    )
    # user have the download right
    if constants.rights['download']['id'] in right_ids:
        debug('Download', 1)
        return hoover_actions(
            helpers.export_link(track.id, url('/tracks'))
    )
    # user have upload right
    if constants.rights['upload']['id'] in right_ids:
        debug('Upload', 1)
        return hoover_actions(
            helpers.edit_link(track.id, url('/tracks'))
    )
    debug('no rights', 1)
    return hoover_actions('')


def track_grid_permissions(user=None, rights=None, project=None):
    # hidden info on the track
    h_info = lambda obj: hide_info({
        'tr_id': obj.id,
        'tr_status': obj.status,
        'tr_color': helpers.get_track_color(obj),
        })
    debug('Track grid permissions with %s' % rights)
    return twf.DataGrid(fields=[('Name', 'name'),
        (hoover_action, lambda obj: get_actions(obj, user, rights, project)),
        ('Color', lambda obj: genshi.Markup(helpers.track_color(obj))),
        ('Owner', 'owner'),
        ('Created', 'created'),
        ('Assembly', 'sequence'),
        ('Type', 'vizu'),
        (hidden_info, h_info),
    ])


def track_grid_user(user, project=None):
    return twf.DataGrid(fields=[
    ('Name', 'name'),
    (hoover_action, lambda obj: hoover_actions(
            helpers.export_link(obj.id, url('/tracks'), project=project)
            + helpers.edit_link(obj.id, url('/tracks'), project=project)
            + helpers.delete_link(obj.id, url('/tracks'), project=project)
    )),
    ('Color', lambda obj: genshi.Markup(helpers.track_color(obj))),
    ('Owner', 'owner'),
     ('Created', 'created'),
     ('Assembly', 'sequence'),
     ('Type', 'vizu'),
    (hidden_info, lambda obj: hide_info({
        'tr_id': obj.id,
        'tr_status': obj.status,
        })),
    ])


track_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    (hoover_action, lambda obj: hoover_actions(
            helpers.export_link(obj.id, url('/tracks'))
            + helpers.edit_link(obj.id, url('/tracks'))
            + helpers.delete_link(obj.id, url('/tracks'))
    )),
    ('Color', lambda obj: genshi.Markup(helpers.track_color(obj))),
     ('Created', 'created'),
     ('Assembly', 'sequence'),
     ('Type', 'vizu'),
    (hidden_info, lambda obj: hide_info({
        'tr_id': obj.id,
        'tr_status': obj.status,
        })),
    ])


def etrack_grid_permissions(rights=None):
    if rights is not None:
        del_action = None
        right_ids = [r.id for r in rights]
        if constants.rights['download']['id'] in right_ids and constants.rights['upload']['id'] in right_ids:
            actions = lambda obj: hoover_actions(
                helpers.export_link(obj.id, url('/tracks'))
                #+ helpers.edit_link(obj.id, url('/tracks'))
                #+ helpers.delete_link(obj.id, url('/tracks'))
                )
        elif constants.rights['download']['id'] in right_ids:
            actions = lambda obj: hoover_actions(
                helpers.export_link(obj.id, url('/tracks')))
        elif constants.rights['upload']['id'] in right_ids:
            actions = lambda obj: hoover_actions(
                helpers.edit_link(obj.id, url('/tracks'))
                + helpers.delete_link(obj.id, url('/tracks')))
        else:
            actions = lambda obj: hoover_actions('')

        h_info = lambda obj: hide_info({
            'tr_id': obj.id,
            'tr_status': obj.status,
            'tr_color': helpers.get_track_color(obj),
            })


        fields = [ ('Name', 'name'),
        (hoover_action, actions),
        ('Created', 'created'),
        ('Assembly', 'sequence'),
        ('Type', 'vizu'),
        (hidden_info, h_info),
        ]

    return twf.DataGrid(fields=fields)



track_admin_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    (hoover_action, lambda obj: hoover_actions(
        helpers.export_link(obj.id, url('/tracks'), img_src='../../images/export.png')
        + helpers.edit_link(obj.id, url('/tracks'), img_src='../../images/pencil.png')
        + helpers.delete_link(obj.id, url('/tracks'), img_src='../../images/delete.png')
    )),
    ('User', 'user.email'),
    ('Created', 'created'),
    ('Assembly', 'sequence'),
    ('Type', 'vizu'),
    (hidden_info, lambda obj: hide_info({
        'tr_id': obj.id,
        'tr_status': obj.status,
        })),


])


project_grid = twf.DataGrid(fields = [
        ('Name', 'name'),
        (hidden_info,lambda obj: hide_info({
                    'tr_actions':
        helpers.get_view_link(obj.id, 'project_id', constants.full_rights)
                    + helpers.share_link(obj.id)
                    #+ helpers.get_copy_project_link(obj.id, constants.full_rights)
                    + helpers.edit_link(obj.id, url('/projects'))
                    #+ helpers.get_detail_link(obj.id, 'project_id', constants.full_rights)
                    })),
        ('Created', 'created'),
        ('Assembly', 'assembly'),
        ('Track', 'get_tracks'),
        (hidden_info,lambda obj: hide_info({
        'tr_actions':  helpers.delete_link(obj.id),
        }))
        ])


project_list= twf.DataGrid(fields = [
        ('Projects', lambda obj: genshi.Markup(helpers.project_link(obj.name, obj.id))),
])

project_sharing = twf.DataGrid(fields=[
        ('Circle', 'circle.display'),
        ('Rights', lambda obj:genshi.Markup(
                get_project_right_sharing_form(obj)))
        ])


def get_project_right_sharing_form(circle_right):
    options = ['Read', 'Download', 'Upload']
    sstr = '''
    <form class="required rightsharingform" method="post" action="%s">
    <div><input type="hidden" value="%s" name='cid' class="hiddenfield"></div>
    <div><input type="hidden" value="true" name='rights' class="hiddenfield"></div>
    <div><input type="hidden" value="%s" name='pid' class="hiddenfield"></div>
    <table cellspacing="0" cellpadding="2" border="0">
    <tbody><tr title="" id="rights_checkboxes.container">
    <td class="fieldcol"><table class="checkboxtable" id="rights_checkboxes">
    <tbody><tr> ''' % (url('/projects/share/%s' % circle_right.project_id), circle_right.circle.id, circle_right.project_id)

    for opt in options:
        sstr += '<td>' + get_right_checkbok(circle_right, opt) + '</td>'

    sstr += '''
            </tr></tbody></table></td>
            <td class="fieldcol" id="submit.container">
            <input type="submit" value="change rights" class="submitbutton">
            </td></tr></tbody></table>
        </form>
'''
    return sstr


def get_right_checkbok(obj, right_name):
    rights = obj.rights
    checked = False
    for right in rights:
        if right.name.lower() == right_name.lower():
            checked = True
    str = '''
    <input type="checkbox" name="rights_checkboxes" value="%s"

''' % (right_name)

    if checked:
        str += ' checked="yes"'
    str += '/><label >%s</label>' % (right_name)
    return str

circle_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    (hoover_action, lambda obj: hoover_actions(
        helpers.edit_link(obj.id, url('/circles'))
        + helpers.delete_link(obj.id, url('/circles'))
    )),
    ('Description', 'description'),
    ('Members', 'get_users'),
])

circle_description_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    (hoover_action,lambda obj: hoover_actions(
            helpers.get_delete_circle_description_link(obj.id, obj.cid)
    )),
    ('Firstname', 'firstname'),
    ('Email', 'email'),
    
])

sequence_user_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
        (hoover_action,lambda obj: hoover_actions(
        helpers.get_remove_user_from_sequence_link(obj.id, obj.sid)
    )),
    ('Firstname', 'firstname'),
    ('Email', 'email')
])

sequence_default_tracks = twf.DataGrid(fields=[
    ('Name', 'name'),
        (hoover_action, lambda obj: hoover_actions(
        helpers.edit_link(obj.id, url('/tracks'))
        + helpers.get_remove_track_from_sequence_link(obj.id, obj.sid)
    )),
    ('Color', lambda obj: genshi.Markup(helpers.track_color(obj))),
    ('Created', 'created'),
    ('Assembly', 'sequence'),
    ('Type', 'vizu'),
    (hidden_info, lambda obj: hide_info({
        'tr_id': obj.id,
        'tr_status': obj.status,
        })),
])

project_admin_grid = twf.DataGrid(fields=[
    ('Id', 'id'),
    ('Name', 'name'),
    ('User', 'user'),
    ('Created', 'created'),
    ('Assembly', 'assembly'),
    ('Circles', 'get_circle_with_right_display'),
    ('Tracks', 'get_tracks'),
    ('Action', lambda obj:genshi.Markup(
        helpers.get_view_link(obj.id, 'project_id', constants.full_rights)
    ))
])



