'''
Authentication plugin for Tequila Service, provided by EPFL.
see http://tequila.epfl.ch/ for more.

'''
import urllib, urllib2


default_request = {'host':'paprika.epfl.ch',
                             'language' : 'english',
                             'service' : 'GDV',
                             'allows' : 'categorie=SHIBBOLETH',
                             'request':'name firstname email title unit office phone user'}

def create_request(url_access, host,
                   request= default_request):
    '''
    Create the request to be send to Tequila service
    @param url_access: the url where Tequila should send the result
    @param host: the host of the tequila server
    @param wanted_params: the parameters to fetch from tequila server
    '''
    request['urlaccess'] = url_access
    url = 'http://' +host+ '/cgi-bin/tequila/createrequest'
    parameters = '\n'.join([k + '=' + v for k, v in request.iteritems()])
    req = urllib2.Request(url, parameters)
    result = urllib2.urlopen(req).read()
    return result.strip('\n')

def validate_key(key, host):
    '''
    Validate the key on tequila server
    @param key: key - the key to validate
    @param host: the host of the tequila server
    @param return : the user identified
    '''
    url = 'http://'+host+'/cgi-bin/tequila/validatekey'
    request = {'key':key}
    try:
        return urllib2.urlopen( url, urllib.urlencode(request)).read()
    except urllib2.HTTPError :
        return None