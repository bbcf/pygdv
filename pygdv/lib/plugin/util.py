import urllib, urllib2, json
import tg

operation_list = '/form/methods.json'
form_url = '/form/index'

def get_service_url():
    u = tg.config.get('plugin.service.url')
    if u is None:
        raise Exception('no plugin service found. plugin.service.url parameter missing in conf file.')
    return u

def get_form_url():
    return get_service_url() + form_url

def get_plugin_path():
    plugin_sevice_url = get_service_url()
    key = get_shared_key()
    url = plugin_sevice_url + operation_list
    req = urllib2.urlopen(url, data=urllib.urlencode({'key' : key}))
    path = json.load(req)
    return path['paths']



def get_shared_key():
    key = tg.config.get('plugin.shared.key')
    if key is None:
        raise Exception('no plugin key found')
    return key