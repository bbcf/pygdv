'''
Send the response back to the user.
'''
from tg import flash, redirect, error
from pygdv.lib.constants import REQUEST_TYPE, REQUEST_TYPE_COMMAND_LINE


def normal(request, message, redirection, dic):
    '''
    Choose the right return type for a normal response.
    :param request : the request
    :param message : the message to give to the user
    :param redirection : where to redirect the user
    :param dic : the dictionary to return to the user
    '''
    if request.environ[REQUEST_TYPE] == REQUEST_TYPE_COMMAND_LINE:
            dic['message'] = message
            return dic
    flash(message)
    raise redirect(redirection)


def error(request, message, redirection, dic):
    '''
    Choose the right return type for a normal response.
    :param request : the request
    :param message : the message to give to the user
    :param redirection : where to redirect the user
    :param dic : the dictionary to return to the user
    '''
    if request.environ[REQUEST_TYPE] == REQUEST_TYPE_COMMAND_LINE:
            dic['error'] = message
            return dic
    error(message)
    raise redirect(redirection)