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
    #http://127.0.0.1:8080/user_account/?&firstName=chandan&lastName=varma&userEmail=chandan.varma@kiwitech.com&password=chandan@123
    @csrf_exempt
    def user_account(request):
        param_dict = {}
        try:
            profile_data=json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.ReturnErrorResponse(500)
        try:
            User.objects.create_user(first_name=profile_data['firstName'],last_name=profile_data['lastName'],email=profile_data['userEmail'],password=profile_data['password'],username=profile_data['userEmail'])
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
        user = authenticate(username=user_data["username"], password=user_data["password"])
        try:
            user_profile = User.objects.all().values('first_name', 'last_name').filter(username=user)
            list_result = [entry for entry in user_profile]
            result_set = list_result[0]
            token=Token.objects.get(user=user)
            param_dict['message'] = 'success'
            param_dict['user_name'] = user_data["username"]
            param_dict['user_token'] = token.key
            param_dict['first_name']=result_set['first_name']
            param_dict['last_name']=result_set['last_name']
        except:
            return util.returnUnAuthorized()
        return util.returnSuccessShorcut(param_dict)




    def home(request):
        return render(request, 'index.html', {'STATIC_URL': settings.STATIC_URL})


# import json
# from watson_developer_cloud import AlchemyLanguageV1
#
# alchemy_language = AlchemyLanguageV1(api_key='0f1afeb92c657316d12f2b02ff571ea0103c48fb')
# keywords=['python','django']
# print(json.dumps(
#   alchemy_language.combined(
#     text='Chandan Varma is a python developer He has skills in angular js and node js',
#     extract='entities,keywords'),
#   indent=2))

# import requests
# r = requests.get('https://gateway-a.watsonplatform.net/calls/data/GetNews?outputMode=json&start=now-1d&end=now&count=5&q.enriched.url.enrichedTitle.entities.entity=|text=apple,type=company|&return=enriched.url.url,enriched.url.title&apikey=0f1afeb92c657316d12f2b02ff571ea0103c48fb')
# print (r.text)
#The kiwitech Inc company post is hiring a Full Stack Developer for our site team.Skills should be python and django'
