# -*- coding: utf-8 -*-

"""WebHelpers used in pygdv."""

from webhelpers import date, feedgenerator, html, number, misc, text

import genshi
from tg import url
from pygdv.lib import constants


def bioscript(u):
    return '''Your can retrieve analysis result(s) <a href="%s">here</a>.''' % u


def get_circles_edit_link(obj_id, img_src='../images/pencil.png'):
    return '''
    <a class="action" title="edit" href="circles/edit/%s" style="text-decoration:none"><img src="%s" width="16px" height="16px"/></a>
           ''' % (obj_id, img_src)


def edit_link(id, model, img_src='../images/pencil.png', project=None):
    if project is not None:
        id = '%s?pid=%s' % (id, project.id)
    return '''<a class="action" title="edit" href="%s/edit/%s" style="text-decoration:none"><img src="%s" width="16px" height="16px"/>Edit</a>''' % (model, id, img_src)


def share_link(id):
    '''
    Return a HTML share link.
    '''
    return ''' <a class='action share_link' title="share" href="share/%s"></a>''' % id


def project_link(name, id=None):
    if id is None:
        return '''<a class="project_link" href="/tracks">%s</a> ''' % (name)
    return '''<a class="project_link" href="/tracks?pid=%s">%s</a> ''' % (id, name)


def delete_link(id, model, img_src='../images/delete.png', project=None):
    if project is not None:
        id = '%s?pid=%s' % (id, project.id)
    return '''<a class="action" onclick="return confirm('Are you sure?')"; title="delete" href="%s/delete/%s" style="text-decoration:none"><img src="%s"
     width="15px" height="15px"/>Delete</a>''' % (model, id, img_src)


def get_job_results_display(job, u):
    def link(rid, rname):
        return '<a href="%s/result?id=%s">%s</a>' % (u, rid, rname)
    return ', '.join([link(res.id, res.name) for res in job.results])


def get_remove_user_from_sequence_link(user_id, sequence_id):
    return '''<a class="action" onclick="return confirm('Are you sure?')"; title="delete" href="%s" style="text-decoration:none"><img src="images/delete.png"
     width="15px" height="15px"/>Delete</a>''' % (url('/sequences/delete_user', params={'sequence_id': sequence_id, 'user_id': user_id}))


def get_remove_track_from_sequence_link(track_id, sequence_id):
    return '''<a class="action" onclick="return confirm('Are you sure?')"; title="delete" href="%s" style="text-decoration:none"><img src="images/delete.png"
     width="15px" height="15px"/>Delete</a>''' % (url('/sequences/delete_track', params={'track_id': track_id, 'sequence_id': sequence_id}))


def get_delete_circle_description_link(user_id, circle_id):
    return '''<a class="action" onclick="return confirm('Are you sure?')"; title="delete" href="%s" style="text-decoration:none"><img src="images/delete.png"
     width="15px" height="15px"/>Delete</a>''' % (url('/circles/delete_user', params={'id': circle_id, 'user_id': user_id}))

    '''
# <form method="POST" action=%s class="button-to">
#       <input class="action" title="delete" onclick="return confirm('Are you sure?');"
#        value="" style="background-color: transparent; float:left;
#        border:0; color: #286571; display: inline;"type="image" src="../../images/delete.png" width="16px" height="16px"/>
#        Delete
#    <input type="hidden" name='id' value="%s"/>
#        ''' % (action, id)


def export_link(obj_id, model, img_src='../images/export.png', project=None):
    '''
    Return a HTML export link.
    '''
    if project is not None:
        obj_id = '%s?pid=%s' % (obj_id, project.id)
    return ''' <a class='action' title="download the track" href="%s/link/%s"><img src="%s" width="16px" height="16px"/>Download</a>''' % (model, obj_id, img_src)



def tracks(obj):
    if len(obj.tracks)>0:
        return '<div class="htracks"><div class="httitle">Tracks</div>%s</div>' % obj.get_tracks
    return ''
def circles(obj):
    if len(obj.shared_circles)>0:
        return '<div class="hcircles"><div class="httitle">Circles</div>%s</div>' % obj.get_circle_with_right_display
    return ''

def get_delete_link(obj_id, rights = None):
    '''
    Get an HTML delete link for an object.
    @param obj_id: the object_id
    @type obj_id: an integer
    @return: the HTML link
    '''
    if rights is not None and constants.right_upload in rights:
        if rights[constants.right_upload]:
            return '''
    <form method="POST" action=%s class="button-to">
    <input name="_method" value="DELETE" type="hidden"/>
   
    <input class="action delete-button" title="%s" onclick="return confirm('Are you sure?');"
        value="" style="background-color: transparent; float:left;
        border:0; color: #286571; display: inline;"
    type="submit"/>
    </form>
        ''' % (obj_id, 'delete')
    return ''




def get_track_delete_link(obj_id, tmp = False, rights = None):
    if rights is not None and constants.right_upload in rights:
        if rights[constants.right_upload]:
            return '''
    <form method="POST" action=%s class="button-to">
    <input name="_method" value="DELETE" type="hidden"/>
    <input name="tmp" value="%s" type="hidden"/>
    <input class="action delete-button" title="%s" onclick="return confirm('Are you sure?');"
        value="" style="background-color: transparent; float:left;
        border:0; color: #286571; display: inline;"
    type="submit"/>
    </form>
        ''' % (obj_id, tmp, 'delete')
    return ''
    
      
def get_view_link(obj_id, param, rights = None):
    '''
    Return a HTML view link.
    
    '''
    if rights is not None:
        return ''' <a class='action view_link' title="%s" href="%s"></a>''' % ('view', url('./view', params={'project_id':obj_id}))
    return ''


def get_copy_project_link(obj_id, rights=None):
    '''
    Return a HTML export link.
    '''
    
    if rights.get(constants.right_download, False):
        return ''' <a class='action copy_link' title="%s" href="%s"></a>''' % ('copy in your profile', url('/projects/copy', params={'project_id':obj_id}))
    return ''

def get_copy_track_link(obj_id, rights=None):
    '''
    Return a HTML export link.
    '''
    if rights is not None:
        return ''' <a class='action copy_link' title="%s" href="%s"></a>''' % ('copy in your profile', url('/tracks/copy', params={'track_id':obj_id}))
    return ''


def get_track_color(track):
    if track.parameters is not None:
        if 'color' in track.parameters:
            return track.parameters['color']


def track_color(track):
    color = None
    if track.parameters is not None:
        if 'color' in track.parameters:
            color = track.parameters['color']
    if color is None:
        color = constants.default_track_color
    return '''<div class="track-color" style="background-color:%s;"></div>''' % color


def get_export_link(obj_id, param='track_id', rights=None, tmp=False):
    '''
    Return a HTML export link.
    '''
    if tmp:
        return ''
    elif rights is not None:
        return ''' <a class='action export_link' title="%s" href="%s"></a>''' % ('export', url('/tracks/link', params={param:obj_id}))
    return ''

def get_share_link(obj_id, param, rights = None):
    '''
    Return a HTML share link.
    '''
    if rights is not None and constants.right_upload in rights:
        if rights[constants.right_upload]:
            return ''' <a class='action share_link' title="%s" href="%s"></a>''' % ('share with others', url('./share', params={param:obj_id}))
    return ''
                                                        
def get_edit_link(obj_id, rights = None, link='', tmp=False):
    if tmp:
        return ''
    edit = url('%s%s/edit' % (link, obj_id))
    if rights is not None and constants.right_upload in rights:
        if rights[constants.right_upload]:
            return '''
    <a class="action edit_link" title="%s" href="%s%s/edit" style="text-decoration:none"></a>
           ''' % ('edit', link, obj_id)
    return ''



def get_detail_link(obj_id, param, rights = None):
    
    if rights is not None and (constants.right_download in rights and rights[constants.right_download]):
            return '''
    <a class="action detail_link" title="%s" href="%s" style="text-decoration:none"></a>
           ''' % ('details', url('./detail', params={param:obj_id}))
    return ''
       
def get_right_checkbok(obj, right_name):
    circle = obj.circle
    rights = obj.rights
    checked = False
    for right in rights:
        if right.name == right_name: 
            checked = True
    str = '''
    <input type="checkbox" name="rights_checkboxes" value="%s"
   
''' % (right_name)
    
    if checked:
        str+=' checked="yes"'
    str+='/><label >%s</label>' % (right_name)
    return str


'''
<input type="checkbox" name="rights_checkboxes" value="Download" id="rights_checkboxes_1">
                        <label for="rights_checkboxes_1">Download</label>
                        </td><td>
                        <input type="checkbox" name="rights_checkboxes" value="Upload" id="rights_checkboxes_2">
                        <label for="rights_checkboxes_2">Upload</label>
                        '''



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
        str += '<td>' + get_right_checkbok(circle_right, opt) + '</td>'

    str += '''
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


def get_task_status(track=None):
    '''
    Get a output for the status of a task: a link to the traceback if the status is ``FAILURE``,
    else the string representing the status.
    @param track: the track to get the status from
    '''
    obj = track
    if obj.status != constants.ERROR:
        return obj.status
    return genshi.Markup('<a href="%s">%s</a>' % (url('./traceback', params={'track_id': obj.id, 'tmp': obj.tmp}),
                                                  constants.ERROR
                                                  ))
