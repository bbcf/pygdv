from pygdv.lib import constants, helpers
import tw.forms as twf
import genshi, json


hidden_info = genshi.Markup("<span class='table_hidden'>hidden_info</span>")


def hide_info(dict):
    span=''
    for k, v in dict.iteritems():
        span +="<span class=%s>%s</span>" % (k, v)

    return genshi.Markup("<span class='table_hidden'>%s</span>" % span)




track_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    ('Created', 'created'),
    ('Assembly', 'sequence'),
    ('Type', 'vizu'),
    (hidden_info, lambda obj : hide_info({
        'tr_id' : obj.id,
        'tr_status': obj.status,
        'tr_actions' :
        helpers.get_export_link(obj.id, rights = constants.full_rights, tmp=obj.tmp)
        + helpers.get_edit_link(obj.id, rights = constants.full_rights, link='./', tmp=obj.tmp)
        + helpers.get_track_delete_link(obj.id, obj.tmp, rights = constants.full_rights)
    }))
])

project_grid = twf.DataGrid(fields = [
    ('Name', 'name'),
    ('Created', 'created'),
    ('Assembly', 'assembly'),
    (hidden_info,lambda obj : hide_info({
        'tr_actions' :
        helpers.get_view_link(obj.id, 'project_id', constants.full_rights)
        + helpers.get_share_link(obj.id, 'project_id', constants.full_rights)
        #+ helpers.get_copy_project_link(obj.id, constants.full_rights)
        + helpers.get_edit_link(obj.id, constants.full_rights)
        + helpers.get_delete_link(obj.id, constants.full_rights)
        #+ helpers.get_detail_link(obj.id, 'project_id', constants.full_rights)

    }) ),
])


circle_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    ('Description', 'description'),
    ('Owner', 'creator'),
    ('Members', 'get_users'),
    (hidden_info,lambda obj : hide_info({
        'tr_actions' :
            helpers.get_delete_link(obj.id, rights = constants.full_rights)
            + helpers.get_circles_edit_link(obj.id)
        }))
])

