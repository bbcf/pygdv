from pygdv.lib import constants, helpers
import tw.forms as twf
import genshi


hidden_info = genshi.Markup("<div class='table_hidden'>hidden_info</div>")


def hide_info(dict):
    span=''
    for k, v in dict.iteritems():
        span +="<div class='table_hidden %s'>%s</div>" % (k, v)

    return genshi.Markup("<div class='hidden_info'>%s</div>" % span)




track_grid = twf.DataGrid(fields=[
    ('Name', 'name'),
    (hidden_info, lambda obj : hide_info({
                    'tr_id' : obj.id,
                    'tr_status': obj.status,
                    'tr_color' : helpers.get_track_color(obj),
                    'tr_actions' :
                        helpers.get_export_link(obj.id, rights = constants.full_rights, tmp=obj.tmp)
                    + helpers.get_edit_link(obj.id, rights = constants.full_rights, link='./', tmp=obj.tmp)
                    + helpers.delete_link(obj.id)
                    })),
     ('Created', 'created'),
     ('Assembly', 'sequence'),
     ('Type', 'vizu'),
     
    ])

project_grid = twf.DataGrid(fields = [
        ('Name', 'name'),
        (hidden_info,lambda obj : hide_info({
                    'tr_actions' :
        helpers.get_view_link(obj.id, 'project_id', constants.full_rights)
                    + helpers.share_link(obj.id)
                    #+ helpers.get_copy_project_link(obj.id, constants.full_rights)
                    + helpers.edit_link(obj.id)
        + helpers.delete_link(obj.id)
                    #+ helpers.get_detail_link(obj.id, 'project_id', constants.full_rights)
                    
                    })),
        ('Created', 'created'),
        ('Assembly', 'assembly'),
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
    <form class="required rightsharingform" method="post" action="post_share">
    <div><input type="hidden" value="%s" name='circle_id' class="hiddenfield"></div>
    <div><input type="hidden" value="%s" name='project_id' class="hiddenfield"></div>
    <table cellspacing="0" cellpadding="2" border="0">
        <tbody>
            <tr title="" id="rights_checkboxes.container">
                <td class="fieldcol">
                    <table class="checkboxtable" id="rights_checkboxes">
                        <tbody>
                            <tr>
                                ''' % (circle_right.circle.id, circle_right.project_id)
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
            + helpers.get_circles_edit_link(obj.id)
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

