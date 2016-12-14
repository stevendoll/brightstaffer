from django.conf import settings
from django.http import HttpResponse
import simplejson
import datetime


def returnIntegrityMessage(param_dict={}):
    param_dict['message'] = 'Email id is already exist'
    return returnresponsejson(param_dict)

def returnSuccessShorcut(param_dict={}, httpstatus=200):
    return returnresponsejson(param_dict, httpstatus)

def returnresponsejson(pass_dict, httpstatus=200):
    json_out = simplejson.dumps(pass_dict)
    return HttpResponse(json_out, status=httpstatus, content_type="application/json")

def returnUnAuthorized(param_dict={}):
    param_dict['message'] = 'UnAuthorized User'
    return returnresponsejson(param_dict)

def returnTokenTimeout(param_dict={}):
    param_dict['message'] = 'Email link is no longer valid'
    return returnresponsejson(param_dict)

#
# def retrunEmailError(param_dict={}):
#     param_dict['message'] = 'Email id is not Registered'
#     return returnresponsejson(param_dict)

ERRORPAGE_MAPPING = {
    400:{
        'result':'',
        'message':''
    },
    401:{
        'result':'',
        'message':''
    },
    403:{
        'result':'',
        'message':''
    },
    404:{
        'result':'UnknownEntity',
        'message':'UnknownEntity, Please try again.'
    },
    500:{
        'result':'ServerError',
        'message':'ServerError, Please try again.'
    },
    501:{
        'result':'',
        'message':''
    },
}


def ReturnErrorResponse(status=404, **kwargs):
    msg = kwargs.get('messgage')
    data = {
        'serverStatusCodes': status,
        'currentDate': str(datetime.datetime.now()),
        'result':ERRORPAGE_MAPPING[status]['result'] ,
        'message':ERRORPAGE_MAPPING[status]['message']
    }
    return returnSuccessShorcut(data, httpstatus=status)