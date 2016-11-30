from django.shortcuts import render
from django.conf import settings
from django.db import IntegrityError
from brightStafferapp import util
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
import json

#SignupAPI
#http://127.0.0.1:8080/user_account/?&firstName=chandan&lastName=varma&userEmail=chandan.varma@kiwitech.com&password=chandan@123
@csrf_exempt
def user_account(request):
    param_dict = {}
    try:
        profile_data=json.loads(request.body.decode("utf-8"))
    except ValueError:
        return util.ReturnErrorResponse(500)
    first_name=profile_data['firstName']
    last_name=profile_data['lastName']
    email=profile_data['userEmail']
    password=profile_data['password']
    username=email
    try:
        User.objects.create_user(first_name=first_name,last_name=last_name,email=email,password=password,username=username)
        param_dict['message']='success'
    except IntegrityError:
        return util.returnIntegrityMessage()
    return util.returnSuccessShorcut(param_dict)



#Login API
#http://127.0.0.1:8080/user_login/?username=chandan.varma@kiwitech.com&password=chandan@123
@csrf_exempt
def user_login(request):
    param_dict = {}
    try:
        user_data=json.loads(request.body.decode("utf-8"))
    except ValueError:
        return util.ReturnErrorResponse(500)
    username=user_data["username"]
    password=user_data["password"]
    user = authenticate(username=username, password=password)
    try:
        user_profile = User.objects.all().values('first_name', 'last_name').filter(username=user)
        list_result = [entry for entry in user_profile]
        result_set = list_result[0]
        token=Token.objects.get(user=user)
        param_dict['message'] = 'success'
        param_dict['UserName'] = username
        param_dict['User Token'] = token.key
        param_dict['First Name']=result_set['first_name']
        param_dict['Last Name']=result_set['last_name']
    except:
        return util.returnUnAuthorized()
    return util.returnSuccessShorcut(param_dict)




def home(request):
    return render(request, 'index.html', {'STATIC_URL': settings.STATIC_URL})

