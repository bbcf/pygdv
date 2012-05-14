import urllib, urllib2, json
import tg

operation_list = '/form/methods.json'
form_url = '/form/index'


def get_form_url():
    return tg.config.get('plugin.service.url') + form_url

def get_plugin_path():
    plugin_sevice_url = tg.config.get('plugin.service.url')
    if plugin_sevice_url is None:
        raise Exception('no plugin service found')
    url = plugin_sevice_url + operation_list
    req = urllib2.urlopen(url)
    path = json.load(req)
    return path['paths']



