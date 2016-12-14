from django.conf import settings
from django.http import HttpResponse
import simplejson
import datetime





def returnErrorShorcut(error_code, error_Status, httpstatus=200):
    output = {}
    output['success'] = False
    output['errorcode'] = error_code
    output['errorstring'] = error_Status
    return returnresponsejson(output, httpstatus)


def returnSuccessShorcut(param_dict={}, httpstatus=200):
    param_dict['message'] = 'success'
    return returnresponsejson(param_dict, httpstatus)

def returnresponsejson(pass_dict, httpstatus=200):
    json_out = simplejson.dumps(pass_dict)
    return HttpResponse(json_out, status=httpstatus, content_type="application/json")
