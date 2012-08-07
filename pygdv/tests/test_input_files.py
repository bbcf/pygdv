try:
    import unittest2 as unittest
except ImportError:
    import unittest
from pkg_resources import resource_filename
import os, json
from bbcflib import gdv

samples = {1 : 'features-test.sql', 2 : 'relational-test.sql', 3 : 'signal-test.sql', 4 : 'bed-test.bed',
           5 : 'bedgraph-test.bedgraph', 6 : 'gtf-test.gtf', 7 : 'wig-test.wig', 8 : 'compressed-test.tgz'}

samples_path = resource_filename('pygdv.tests', 'test_files')

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
    with open(logfile, 'a') as l:
        l.write('%s,%s\n' % (key, value))

def upload_fsys(project_id):
    """
    Upload track on GDV via fsys
    """
    mail, key = get_credentials(config_file)
    serv = get_serv(config_file)

    f1 = os.path.join(samples_path, samples[3])
    mess1 = gdv.single_track(mail, key, serv_url=serv, assembly_id=12, fsys=f1)
    t1 = mess1['track_id']
    log('track_id', t1)
    assert mess1['message'] == u'Processing launched.'

    f2 = os.path.join(samples_path, samples[6])
    mess2 = gdv.single_track(mail, key, serv_url=serv, trackname="gtf-test-renamed", project_id=project_id, fsys=f2)
    t2 = mess2['track_id']
    log('track_id', t2)
    assert mess2['message'] == u'Processing launched.'

    return [t1, t2]




def upload_url(project_id):
    mail, key = get_credentials(config_file)
    serv = get_serv(config_file)

    f1 = os.path.join(samples_path, samples[4])
    mess1 = gdv.single_track(mail, key, serv_url=serv, assembly_id=12, url=serv+"/test_files?id=" + str(4), trackname="bed-test-renamed", extension='bed')
    t1 = mess1['track_id']
    log('track_id', t1)
    assert mess1['message'] == u'Processing launched.'

    urls = "%s/test_files?id=%s %s/test_files?id=%s %s/test_files?id=%s" % (serv, 1, serv, 2, serv, 8)
    mess2 = gdv.single_track(mail, key, serv_url=serv, extension='sql', project_id=project_id, url=urls)
    assert mess2['message'] == u'Processing launched.'
    return ['']



def test_input():
    projects = project()
    upload_fsys(projects[0])
    upload_url(projects[1])





def project():
    """
    Create two new project on GDV
    """
    mail, key = get_credentials(config_file)
    serv = get_serv(config_file)

    p2 = gdv.new_project(mail, key, name='test-project2', assembly_id=12, serv_url=serv)
    project_id2 = p2['project']['id']
    log('project_id', project_id2)
    assert p2['message'] == u'Project successfully created.'

    p = gdv.new_project(mail, key, name='test-project', assembly_id=12, serv_url=serv)
    project_id = p['project']['id']
    log('project_id', project_id)
    assert p['message'] == u'Project successfully created.'
    return [project_id, project_id2]














