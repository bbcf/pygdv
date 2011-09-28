# -*- coding: utf-8 -*-

"""WebHelpers used in pygdv."""

from webhelpers import date, feedgenerator, html, number, misc, text


def get_delete_link(obj_id):
    '''
    Get an HTML delete link for an object.
    @param obj_id: the object_id
    @type obj_id: an integer
    @return: the HTML link
    '''
    return '''
    <form method="POST" action=%s class="button-to">
    <input name="_method" value="DELETE" type="hidden"/>
   
    <input class="delete-button" onclick="return confirm('Are you sure?');" 
        value="delete" style="background-color: transparent; float:left; 
        border:0; color: #286571; display: inline; margin: 0; padding: 0;" 
    type="submit"/>
    </form>
        ''' % (obj_id)
        
        
        
def get_edit_link(obj_id):
    return '''
    <a class="edit_link" href="%s/edit" style="text-decoration:none"></a>
           ''' %(obj_id)
           
           
           
           
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







