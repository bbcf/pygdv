
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from pkg_resources import resource_filename
import os, json
from bbcflib import gdv


config_file = 'test.ini'

logfile = 'logfile.log'


import ConfigParser

def get_credentials(_f):
    config = ConfigParser.ConfigParser()
    config.read(_f)
    m = config.get('MAIN', 'mail')
    k = config.get('MAIN', 'key')
    return m, k

def get_serv(_f):
    config = ConfigParser.ConfigParser()
    config.read(_f)
    s = config.get('MAIN', 'serv')
    return s

def log(key, value):
    """
    log ids in the output files - Tester can view tracks uploaded on GDV, than delete them with the 'delete test'.
    """




def test_delete():
    mail, key = get_credentials(config_file)
    serv = get_serv(config_file)

    with open(logfile, 'r') as l:
        for row in l:
            print row
            k, v = row.split(',')
            if k == 'project_id':
                    mess =  gdv.delete_project(mail, key, v, serv_url=serv)
                    print mess
                    assert mess == {u'message': u'Project successfully deleted.', u'success': u'project deleted'}
            elif k == 'track_id':
                    mess =  gdv.delete_track(mail, key, v, serv_url=serv)
                    print mess
                    assert mess == {u'message': u'Track successfully deleted.', u'success': u'track deleted'}


    os.remove(logfile)




