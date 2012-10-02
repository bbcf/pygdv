
"""
Python helpers to caccess pyGDV from command-line.
All request should have the login on tequila sytem (mail)
and the corresponding key (key) as a parameter.
"""


import json
import urllib
import urllib2


def send_request(url, request, return_type='json'):
    '''
    Send the request to GDV and return the result.
    As JSON or as a request.read().
    :param url: the url of GDV.
    :param request: the request.
    :return: GDV response as json or a stream.
    '''
    req = urllib2.urlopen(url, urllib.urlencode(request))
    if return_type == 'json':
        return json.load(req)
    return req.read()


def new_project(mail, key, name, assembly_id, serv_url):
    '''
    Create a new project on GDV.
    :param name : name of the project
    :param assembly_id : the assembly identifier in GenRep (must be BBCF_VALID)
    :param serv_url : GDV url.
    :return a JSON
    '''
    query_url = '%s/%s' % (serv_url, 'projects/create')
    request = {'mail': mail,
               'key': key,
               'name': name,
               'assembly': assembly_id
               }
    return send_request(query_url, request)


def get_project(mail, key, project_key, serv_url):
    '''
    Get a project by it's key.
    :param project_key : the project key
    '''
    query_url = '%s/%s' % (serv_url, 'projects/get')
    request = {'mail': mail,
               'key': key,
               'project_key': project_key
               }
    return send_request(query_url, request)


def delete_project(mail, key, project_id, serv_url):
    query_url = '%s/%s/%s' % (serv_url, 'projects/delete', project_id)
    request = {'mail': mail,
               'key': key}
    return send_request(query_url, request)


def delete_track(mail, key, track_id, serv_url):
    query_url = '%s/%s/%s' % (serv_url, 'tracks/delete', track_id)
    request = {'mail': mail,
               'key': key}
    return send_request(query_url, request)


def single_track(mail, key, serv_url,
                 assembly_id=None, project_id=None,
                 url=None, fsys=None, trackname=None, extension=None,
                 force=False, delfile=False):
    '''
    Create a new track on GDV.
    :param name : name of the project.
    :param assembly_id : the assembly identifier in GenRep.
    Could be optional if a project_id is specified.
    :param project_id : the project identifier to add the track to.
    :param url : an url pointing to a file.
    :param extension : extension of the file provided.
    :param fsys : if the file is on the same file system, a filesystem path
    :param trackname : the name to give to the track.
    :param force : A boolean. Force the file to be recomputed.
    :param delfile : If true and file comming from fsys,
    the original file will be removed after job success.
    :return a JSON
    '''
    query_url = '%s/%s' % (serv_url, 'tracks/create')
    request = {'mail': mail, 'key': key}
    if assembly_id:
        request['assembly'] = assembly_id
    if project_id:
        request['project_id'] = project_id
    if url:
        request['url'] = url
    if fsys:
        request['fsys'] = fsys
    if trackname:
        request['trackname'] = trackname
    if force:
        request['force'] = force
    if extension:
        request['extension'] = extension
    if delfile:
        request['delfile'] = delfile
    return send_request(query_url, request)



#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
