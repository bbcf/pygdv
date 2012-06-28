from pygdv.lib import constants, helpers
import tw.forms as twf
import genshi
from tg import url


hidden_info = genshi.Markup("<div class='table_hidden'>hidden_info</div>")


def hide_info(dict):
    span=''
    for k, v in dict.iteritems():
        span +="<div class='table_hidden %s'>%s</div>" % (k, v)

    return genshi.Markup("<div class='hidden_info'>%s</div>" % span)


job_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    ('Description', 'description'),
    ('Output', 'output_display'),
    (hidden_info, lambda obj : hide_info({
        'tr_status': obj.status,
        'tr_actions' : helpers.delete_link(obj.id, action='.'),
        'tr_info' : obj.traceback
    }))
])




def track_grid_permissions(rights=None):
    if rights is not None:
        del_action = None
        right_ids = [r.id for r in rights]
        if constants.right_download_id in right_ids and constants.right_upload_id in right_ids:
            actions = lambda obj : hide_info({
                'tr_id' : obj.id,
                'tr_status': obj.status,
                'tr_color' : helpers.get_track_color(obj),
                'tr_actions' :
                    helpers.export_link(obj.id)
                    + helpers.edit_link(obj.id, url('/tracks')),
                })
            del_action =  lambda obj : hide_info({
                'tr_actions' :
                    helpers.delete_link(obj.id)})

        elif  constants.right_download_id in right_ids:
            actions = lambda obj : hide_info({
                'tr_id' : obj.id,
                'tr_status': obj.status,
                'tr_color' : helpers.get_track_color(obj),
                'tr_actions' :
                    helpers.export_link(obj.id)
                })
        elif constants.right_upload_id in right_ids:
            actions = lambda obj : hide_info({
                'tr_id' : obj.id,
                'tr_status': obj.status,
                'tr_color' : helpers.get_track_color(obj),
                'tr_actions' :
                    helpers.edit_link(obj.id, url('/tracks')),
                })
            del_action =  lambda obj : hide_info({
                'tr_actions' :
                    helpers.delete_link(obj.id)})
        else :
            actions = lambda obj : hide_info({
                'tr_id' : obj.id,
                'tr_status': obj.status,
                'tr_color' : helpers.get_track_color(obj),
                })

        fields = [ ('Name', 'name'),
        (hidden_info, actions),
        ('Created', 'created'),
        ('Assembly', 'sequence'),
        ('Type', 'vizu'),
        ]
        if del_action is not None:
            fields.append((hidden_info, del_action))
    return twf.DataGrid(fields=fields)

track_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    (hidden_info, lambda obj : hide_info({
                    'tr_id' : obj.id,
                    'tr_status': obj.status,
                    'tr_color' : helpers.get_track_color(obj),
                    'tr_actions' :
                        helpers.export_link(obj.id)
                    + helpers.edit_link(obj.id, url('/tracks')),
                    })),
     ('Created', 'created'),
     ('Assembly', 'sequence'),
     ('Type', 'vizu'),
    (hidden_info, lambda obj : hide_info({
        'tr_actions' :
        helpers.delete_link(obj.id)
    })),
    ])

track_read_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    (hidden_info, lambda obj : hide_info({
        'tr_id' : obj.id,
        'tr_status': obj.status,
        'tr_color' : helpers.get_track_color(obj),
        'tr_actions' :
            helpers.export_link(obj.id)
            + helpers.edit_link(obj.id, url('/tracks')),
        })),
    ('Created', 'created'),
    ('Assembly', 'sequence'),
    ('Type', 'vizu'),
    (hidden_info, lambda obj : hide_info({
        'tr_actions' :
            helpers.delete_link(obj.id)
    })),
])






project_grid = twf.DataGrid(fields = [
        ('Name', 'name'),
        (hidden_info,lambda obj : hide_info({
                    'tr_actions' :
        helpers.get_view_link(obj.id, 'project_id', constants.full_rights)
                    + helpers.share_link(obj.id)
                    #+ helpers.get_copy_project_link(obj.id, constants.full_rights)
                    + helpers.edit_link(obj.id, url('/projects')),
                    #+ helpers.get_detail_link(obj.id, 'project_id', constants.full_rights)
                    })),
        ('Created', 'created'),
        ('Assembly', 'assembly'),
        ('Track', 'get_tracks'),
        (hidden_info,lambda obj : hide_info({
        'tr_actions' :  helpers.delete_link(obj.id),
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


def get_right_checkbok(obj, right_name):
    circle = obj.circle
    rights = obj.rights
    checked = False
    for right in rights :
        if right.name == right_name :
            checked = True
    str = '''
    <input type="checkbox" name="rights_checkboxes" value="%s"

''' % (right_name)

    if checked :
        str+=' checked="yes"'
    str+='/><label >%s</label>' % (right_name)
    return str

def get_project_right_sharing_form(circle_right):
    options = ['Read', 'Download', 'Upload']
    str = '''
    <form class="required rightsharingform" method="post" action="%s">
    <div><input type="hidden" value="%s" name='cid' class="hiddenfield"></div>
    <div><input type="hidden" value="true" name='rights' class="hiddenfield"></div>
    <div><input type="hidden" value="%s" name='pid' class="hiddenfield"></div>
    <table cellspacing="0" cellpadding="2" border="0">
        <tbody>
            <tr title="" id="rights_checkboxes.container">
                <td class="fieldcol">
                    <table class="checkboxtable" id="rights_checkboxes">
                        <tbody>
                            <tr>
                                ''' % (url('/projects/share/%s' % circle_right.project_id), circle_right.circle.id, circle_right.project_id)
    for opt in options:
        str+='<td>'+get_right_checkbok(circle_right, opt)+'</td>'


    str+='''

                            </tr>
                        </tbody>
                    </table>
                </td>
            <td class="fieldcol" id="submit.container">
                <input type="submit" value="change rights" class="submitbutton">
            </td>
        </tr>
    </tbody></table>
</form>
'''
    return str




circle_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    (hidden_info,lambda obj : hide_info({
        'tr_actions' :
            helpers.get_delete_link(obj.id, rights = constants.full_rights)
            + helpers.edit_link(obj.id, url('/circles'))
        })),
    ('Description', 'description'),
    ('Members', 'get_users'),
    
])

circle_description_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    (hidden_info,lambda obj : hide_info({
        'tr_actions' :
            helpers.get_delete_circle_description_link(obj.id, obj.cid)
    })),
    ('Firstname', 'firstname'),
    ('Email', 'email'),
    
])

