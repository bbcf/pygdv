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
    <input name="_method" value="DELETE" type="hidden">
    <input class="delete-button" onclick="return confirm('Are you sure?');" 
        value="delete" style="background-color: transparent; float:left; 
        border:0; color: #286571; display: inline; margin: 0; padding: 0;" 
    type="submit">
    </form>
        ''' % (obj_id)