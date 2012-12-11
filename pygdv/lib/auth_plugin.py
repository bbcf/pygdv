'''
The authentication plugins for login in the application.
They are called in the 'who.ini' file
'''
import datetime
from codecs import utf_8_decode
from codecs import utf_8_encode
import os
import time
import tg

from paste.httpheaders import REQUEST_METHOD
from paste.request import get_cookies
from paste.auth import auth_tkt
from webob import Request, Response
from repoze.who.utils import resolveDotted
from zope.interface import implements
from pygdv import handler
from pygdv.lib import constants

from repoze.who.interfaces import IIdentifier, IChallenger, IAuthenticator, IRequestClassifier
import zope.interface

_NOW_TESTING = None  # unit tests can replace
def _now():  #pragma NO COVERAGE
    '''
    For unit tests purpose
    '''
    if _NOW_TESTING is not None:
        return _NOW_TESTING
    return datetime.datetime.now()

def make_plugin(secret=None,
                secretfile=None,
                cookie_name='auth_tkt',
                secure=False,
                include_ip=True,
                timeout=None,
                reissue_time=None,
                userid_checker=None,
               ):
    '''
    Build the identifier plugin
    '''
   
    if (secret is None and secretfile is None):
        raise ValueError("One of 'secret' or 'secretfile' must not be None.")
    if (secret is not None and secretfile is not None):
        raise ValueError("Specify only one of 'secret' or 'secretfile'.")
    if secretfile:
        secretfile = os.path.abspath(os.path.expanduser(secretfile))
        if not os.path.exists(secretfile):
            raise ValueError("No such 'secretfile': %s" % secretfile)
        secret = open(secretfile).read().strip()
    if timeout:
        timeout = int(timeout)
    if reissue_time:
        reissue_time = int(reissue_time)
    if userid_checker is not None:
        userid_checker = resolveDotted(userid_checker)
    plugin = CustomCookiePlugin(secret,
                                 cookie_name,
                                 _bool(secure),
                                 _bool(include_ip),
                                 timeout,
                                 reissue_time,
                                 userid_checker,
                                 )
    return plugin



def make_plugin_auth(check_fn=None):
    return CustomAuthPlugin(check_fn)



def make_plugin_cl(*args, **kw):
    return CustomCommandLinePlugin()







class CustomCookiePlugin(object):
    '''
    A custom cookie plugin for authentication.
    '''
    implements(IIdentifier, IChallenger)
   
    userid_type_decoders = {
        'int':int,
        'unicode':lambda x: utf_8_decode(x)[0],
        }

    userid_type_encoders = {
        int: ('int', str),
        long: ('int', str),
        unicode: ('unicode', lambda x: utf_8_encode(x)[0]),
        }
    
  
    def __init__(self, secret, cookie_name='auth_tkt',
                 secure=False, include_ip=False,
                 timeout=None, reissue_time=None, userid_checker=None):
        self.secret = secret
        self.cookie_name = cookie_name
        self.include_ip = include_ip
        self.secure = secure
        if timeout and ( (not reissue_time) or (reissue_time > timeout) ):
            raise ValueError('When timeout is specified, reissue_time must '
                             'be set to a lower value')
        self.timeout = timeout
        self.reissue_time = reissue_time
        self.userid_checker = userid_checker

    # IIdentifier
    def identify(self, environ):
        '''
        Identify the user
        '''

        remotes = environ['REMOTE_ADDR'].split(', ')
        environ['REMOTE_ADDR'] = remotes[0]

        environ['auth'] = False
        cookies = get_cookies(environ)
        cookie = cookies.get(self.cookie_name)

        if cookie is None or not cookie.value:
            return None

        if self.include_ip:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'
        
        try:
            timestamp, userid, tokens, user_data = auth_tkt.parse_ticket(
                self.secret, cookie.value, remote_addr)
        except auth_tkt.BadTicket:
            return None

        if self.userid_checker and not self.userid_checker(userid):
            return None

        if self.timeout and ( (timestamp + self.timeout) < time.time() ):
            return None

        userid_typename = 'userid_type:'
        user_data_info = user_data.split('|')
        for datum in filter(None, user_data_info):
            if datum.startswith(userid_typename):
                userid_type = datum[len(userid_typename):]
                decoder = self.userid_type_decoders.get(userid_type)
                if decoder:
                    userid = decoder(userid)
            
        environ['REMOTE_USER_TOKENS'] = tokens
        environ['REMOTE_USER_DATA'] = user_data
        environ['AUTH_TYPE'] = 'cookie'

        identity = {}
        identity['timestamp'] = timestamp
        identity['repoze.who.userid'] = userid
        identity['tokens'] = tokens
        identity['userdata'] = user_data
        environ['auth'] = True
        return identity

    def _get_cookies(self, environ, value, max_age=None):
        '''
        Get the cookie from the environ.
        '''
        if max_age is not None:
            max_age = int(max_age)
            later = _now() + datetime.timedelta(seconds=max_age)
            # Wdy, DD-Mon-YY HH:MM:SS GMT
            expires = later.strftime('%a, %d %b %Y %H:%M:%S')
            # the Expires header is *required* at least for IE7 (IE7 does
            # not respect Max-Age)
            max_age = "; Max-Age=%s; Expires=%s" % (max_age, expires)
        else:
            max_age = ''

        cur_domain = environ.get('HTTP_HOST', environ.get('SERVER_NAME'))
        wild_domain = '.' + cur_domain
        cookies = [
            ('Set-Cookie', '%s="%s"; Path=/%s' % (
            self.cookie_name, value, max_age)),
            ('Set-Cookie', '%s="%s"; Path=/; Domain=%s%s' % (
            self.cookie_name, value, cur_domain, max_age)),
            ('Set-Cookie', '%s="%s"; Path=/; Domain=%s%s' % (
            self.cookie_name, value, wild_domain, max_age))
            ]
        return cookies

    # IIdentifier
    def forget(self, environ, identity):
        '''
        Forget the user (delete the cookies)
        '''
        # return a set of expires Set-Cookie headers
        #identity = None
        return self._get_cookies(environ, 'INVALID', 0)
    
    # IIdentifier
    def remember(self, environ, identity):
        '''
        Remember the user.
        '''
        if self.include_ip:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'

        cookies = get_cookies(environ)
        #old_cookie = cookies.get(self.cookie_name)
        existing = cookies.get(self.cookie_name)
        old_cookie_value = getattr(existing, 'value', None)
        max_age = identity.get('max_age', None)

        timestamp, userid, tokens, userdata = None, '', '', ''

        if old_cookie_value:
            try:
                timestamp, userid, tokens, userdata = auth_tkt.parse_ticket(
                    self.secret, old_cookie_value, remote_addr)
            except auth_tkt.BadTicket:
                pass

        who_userid = identity['repoze.who.userid']
        who_tokens = identity.get('tokens', '')
        who_userdata = identity.get('userdata', '')

        encoding_data = self.userid_type_encoders.get(type(who_userid))
        if encoding_data:
            encoding, encoder = encoding_data
            who_userid = encoder(who_userid)
            who_userdata = 'userid_type:%s' % encoding
        
        if not isinstance(tokens, basestring):
            tokens = ','.join(tokens)
        if not isinstance(who_tokens, basestring):
            who_tokens = ','.join(who_tokens)
        old_data = (userid, tokens, userdata)
        new_data = (who_userid, who_tokens, who_userdata)

        if old_data != new_data or (self.reissue_time and
                ( (timestamp + self.reissue_time) < time.time() )):
            ticket = auth_tkt.AuthTicket(
                self.secret,
                who_userid,
                remote_addr,
                tokens=who_tokens,
                user_data=who_userdata,
                cookie_name=self.cookie_name,
                secure=self.secure)
            new_cookie_value = ticket.cookie_value()
            
            #cur_domain = environ.get('HTTP_HOST', environ.get('SERVER_NAME'))
            #wild_domain = '.' + cur_domain
            if old_cookie_value != new_cookie_value:
                # return a set of Set-Cookie headers
                return self._get_cookies(environ, new_cookie_value, max_age)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__,
                            id(self)) #pragma NO COVERAGE

    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        '''
        The challenger.
        '''
        cookies = get_cookies(environ)
        cookie = cookies.get(self.cookie_name)
    # request = Request(environ)
        if cookie is None or not cookie.value:
            pass
        # redirect to login_form
        res = Response()
        res.status = 302
        addon = None
        if 'SCRIPT_NAME' in environ:
            addon = environ['SCRIPT_NAME']
        if addon is not None:
            res.location = addon + '/login_needed'
        else :
            res.location = 'login_needed'
        return res
            


def _bool(value):
    '''
    Yes, true or 1 => True
    '''
    if isinstance(value, basestring):
        return value.lower() in ('yes', 'true', '1')
    return value





class CustomAuthPlugin(object):
    '''
    A custom authenticator.
    '''
    implements(IAuthenticator)
    def __init__(self, check):
        self.check = check
    # IAuthenticatorPlugin
    def authenticate(self, environ, identity):
        '''
        Authenticate
        '''
        pass
    
    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__,
                            id(self)) #pragma NO COVERAGE




class CustomCommandLinePlugin(object):
    '''
    A custom plugin for authentication from command line.
    '''
    implements(IIdentifier, IChallenger)
    # IIdentifier
    def identify(self, environ):
        '''
        Identify the user
        '''
        request = Request(environ)

        if 'mail' in request.str_POST and 'key' in request.str_POST:
            user = handler.user.get_user(request.str_POST['key'], request.str_POST['mail'])
            if user is None : return {}
            identity = {}
            identity['repoze.who.userid'] = user.email
            environ['auth'] = True
            return identity
        return None

    # IIdentifier
    def forget(self, environ, identity):
        '''
        Forget the user
        '''
        pass
    # IIdentifier
    def remember(self, environ, identity):
        '''
        Remember the user. (no remember from command line)
        '''
        
    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        '''
        The challenger.
        '''
        res = Response()
        res.headerlist = [('Content-type', 'application/json')]
        res.charset = 'utf8'
        res.unicode_body = u"{error:'wrong credentials'}"
        res.status = 403
        return res
   
   




def request_classifier(environ):
    '''
    Returns one of the classifiers 'command_line' or 'browser',                                                                                                                                     
    depending on the imperative logic below
    '''
    request_method = REQUEST_METHOD(environ)
    if request_method == 'POST':
        req = Request(environ)
        if not 'Cookie' in req.headers:
            environ[constants.REQUEST_TYPE] = constants.REQUEST_TYPE_COMMAND_LINE
            return constants.REQUEST_TYPE_COMMAND_LINE
    environ[constants.REQUEST_TYPE] = constants.REQUEST_TYPE_BROWSER
    return constants.REQUEST_TYPE_BROWSER
zope.interface.directlyProvides(request_classifier, IRequestClassifier)






