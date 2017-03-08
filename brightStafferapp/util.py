from django.conf import settings
from django.http import HttpResponse
import simplejson
from django.http import HttpResponseBadRequest
from functools import wraps
from django.utils.decorators import available_attrs
import json


def returnErrorShorcut(error_code, error_Status, httpstatus=200):
    output = dict()
    output['success'] = False
    output['errorcode'] = error_code
    output['errorstring'] = error_Status
    return returnresponsejson(output, httpstatus)


def returnSuccessShorcut(param_dict, httpstatus=200):
    param_dict['message'] = 'success'
    return returnresponsejson(param_dict, httpstatus)


def returnresponsejson(pass_dict, httpstatus=200):
    json_out = simplejson.dumps(pass_dict)
    return HttpResponse(json_out, status=httpstatus, content_type="application/json")


def require_post_params(params):
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(request, *args, **kwargs):
            if not all(param in json.loads(request.request.body.decode('utf-8')) for param in params):
                return HttpResponseBadRequest("Required parameters not found.")
            return func(request, *args, **kwargs)
        return inner
    return decorator


def required_post_params(params):
    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(request, *args, **kwargs):
            if not all(param in request.request.POST for param in params):
                return HttpResponseBadRequest("Required parameters not found.")
            return func(request, *args, **kwargs)
        return inner
    return decorator
