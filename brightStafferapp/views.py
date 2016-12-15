from django.shortcuts import render
from django.conf import settings
from django.db import IntegrityError
from brightStafferapp import util
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
import json



class UserData():

    #SignupAPI
    @csrf_exempt
    def user_account(request):
        param_dict = {}
        try:
            profile_data=json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(500,'Invalid Forrm Fields')
        try:
            User.objects.create_user(first_name=profile_data['firstName'],last_name=profile_data['lastName'],email=profile_data['userEmail'],password=profile_data['password'],username=profile_data['userEmail'])
        except IntegrityError:
            return util.returnErrorShorcut(500,'Email id is already exist')
        return util.returnSuccessShorcut(param_dict)



    #Login API
    @csrf_exempt
    def user_login(request):
        param_dict = {}
        try:
            user_data=json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(500,'Invalid Forrm Fields')
        user = authenticate(username=user_data["username"], password=user_data["password"])
        try:
            user_profile = User.objects.all().values('first_name', 'last_name').filter(username=user)
            list_result = [entry for entry in user_profile]
            result_set = list_result[0]
            token=Token.objects.get(user=user)
            param_dict['user_name'] = user_data["username"]
            param_dict['user_token'] = token.key
            param_dict['first_name']=result_set['first_name']
            param_dict['last_name']=result_set['last_name']
        except:
            return util.returnErrorShorcut(500,'UnAuthorized User')
        return util.returnSuccessShorcut(param_dict)




    def home(request):
        return render(request, 'index.html', {'STATIC_URL': settings.STATIC_URL})



