import json

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from brightStafferapp.models import Projects,Concepts
from brightStafferapp import util
from django.views import View
from django.views.generic import View
from django.db.models import Q

class UserData():

    #SignupAPI
    @csrf_exempt
    def user_account(request):
        param_dict = {}
        try:
            profile_data=json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400,'Invalid Forrm Fields')
        try:
            User.objects.create_user(first_name=profile_data['firstName'],last_name=profile_data['lastName'],email=profile_data['userEmail'],password=profile_data['password'],username=profile_data['userEmail'])
            user = authenticate(username=profile_data['userEmail'], password=profile_data["password"])
            token = Token.objects.get(user=user)
            param_dict['first_name']=profile_data['firstName']
            param_dict['last_name']=profile_data['lastName']
            param_dict['user_name'] = profile_data["userEmail"]
            param_dict['user_token'] = token.key
        except IntegrityError:
            return util.returnErrorShorcut(404,'Email id is already exist')
        return util.returnSuccessShorcut(param_dict)



    #Login API
    @csrf_exempt
    def user_login(request):
        param_dict = {}
        try:
            user_data=json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400,'Invalid Forrm Fields')
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
            return util.returnErrorShorcut(401,'UnAuthorized User')
        return util.returnSuccessShorcut(param_dict)




    def home(request):
        return render(request, 'index.html', {'STATIC_URL': settings.STATIC_URL})





class JobPosting():
    @csrf_exempt
    def job_posting(request):
        param_dict={}
        try:
            user_data=json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400,'API parameter is not valid')
        recuriter_email = User.objects.filter(email=user_data['recuriter'])
        recuriter_email_valid=User.objects.filter(email=user_data['recuriter']).exists()
        projects=Projects()
        if recuriter_email_valid == False:
            return util.returnErrorShorcut(404, 'Recuriter email id is not valid')
        values = Token.objects.filter(user=recuriter_email,key=user_data['token']).select_related().exists()
        if values == False:
            return util.returnErrorShorcut(404, 'Access Token is not valid')
        else:
            if user_data['id']=='':
                try:
                    rec_name = User.objects.get(username=user_data['recuriter'])
                    pname_valid = Projects.objects.filter(project_name=user_data['project_name'],recuriter=rec_name).exists()
                    if pname_valid == False:
                        projects.project_name = user_data['project_name']
                        projects.recuriter = rec_name
                        projects.is_published = user_data['is_published']
                        projects.save()
                        p_id = Projects.objects.filter(project_name=user_data['project_name'],
                                                       recuriter=rec_name).values('id')
                        for a_id in p_id:
                            for item, values in a_id.items():
                                param_dict['project_id'] = str(values)
                                return util.returnSuccessShorcut(param_dict)
                    else:
                        return util.returnErrorShorcut(403, 'Project is already exist in database')
                except:
                    return util.returnErrorShorcut(400, 'API parameter is not valid')

            else:
                try:
                    project_id = Projects.objects.filter(id=user_data['id']).exists()
                    if project_id == False:
                        return util.returnErrorShorcut(404, 'Project id is not valid')
                    else:
                        try:
                            del user_data['token']
                            del user_data['recuriter']
                        except KeyError:
                            pass
                        Projects.objects.filter(id=user_data['id']).update(**user_data)
                        return util.returnSuccessShorcut(param_dict)
                except:
                    return util.returnErrorShorcut(400, 'API parameter is not valid')

