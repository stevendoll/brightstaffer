import json
from django.utils import timezone
from watson_developer_cloud import AlchemyLanguageV1
from watson_developer_cloud import WatsonException
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
from brightStaffer.settings import Alchmey_api_key
from json import dumps
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
import ast
from itertools import chain

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

    #This API is returned a previous page info
    @csrf_exempt
    def backButtonInfo(request):
        param_dict = {}
        try:
            user_data = json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400, 'API parameter is not valid')
        recuriter_email = User.objects.filter(email=user_data['recuriter'])
        if not recuriter_email:
            return util.returnErrorShorcut(404, 'Recuriter email id is not valid')
        values = Token.objects.filter(user=recuriter_email, key=user_data['token'])  # .select_related().exists()
        if not values:
            return util.returnErrorShorcut(404, 'Access Token is not valid')
        try:
            project_id = Projects.objects.filter(id=user_data['id'])
            if not project_id:
                return util.returnErrorShorcut(400, 'Project id is not valid')
        except:
            return util.returnErrorShorcut(400, 'Project id is not valid')
        param_dict['project_id'] = user_data['id']
        param_dict['user_token'] = user_data['token']
        param_dict['recuriter'] = user_data['recuriter']
        value = Projects.objects.filter(id=user_data['id']).values()
        for param_value in value:
            if user_data['page']==1:
                param_dict['company_name']=param_value['company_name']
                param_dict['project_name']=param_value['project_name']
                param_dict['location']=param_value['location']
            if user_data['page']==2:
                param_dict['description']=param_value['description']
            if user_data['page']==3:
                concept_dict=Concepts.objects.filter(project=user_data['id']).values('concepts')
                for concept_key in concept_dict:
                    param_dict['concepts']=concept_key['concepts']

        return util.returnSuccessShorcut(param_dict)

    # This API is publish a project
    @csrf_exempt
    def publish(request):
        param_dict = {}
        try:
            user_data = json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400, 'API parameter is not valid')
        recuriter_email = User.objects.filter(email=user_data['recuriter'])
        if not recuriter_email:
            return util.returnErrorShorcut(404, 'Recuriter email id is not valid')
        values = Token.objects.filter(user=recuriter_email, key=user_data['token'])  # .select_related().exists()
        if not values:
            return util.returnErrorShorcut(404, 'Access Token is not valid')
        try:
            project_id = Projects.objects.filter(id=user_data['id'])
            if not project_id:
                return util.returnErrorShorcut(400, 'Project id is not valid')
        except:
            return util.returnErrorShorcut(400, 'Project id is not valid')
        try:
            del user_data['token']
            del user_data['recuriter']
        except KeyError:
            pass
        Projects.objects.filter(id=user_data['id']).update(**user_data)
        Projects.objects.filter(id=user_data['id']).update(create_date=timezone.now())
        return util.returnSuccessShorcut(param_dict)

    # This API is update a concepts
    @csrf_exempt
    def update_concept(request):
        param_dict = {}
        try:
            user_data = json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400, 'API parameter is not valid')
        recuriter_email = User.objects.filter(email=user_data['recuriter'])
        if not recuriter_email:
            return util.returnErrorShorcut(404, 'Recuriter email id is not valid')
        values = Token.objects.filter(user=recuriter_email, key=user_data['token'])  # .select_related().exists()
        if not values:
            return util.returnErrorShorcut(404, 'Access Token is not valid')
        try:
            project_id = Projects.objects.filter(id=user_data['id'])
            if not project_id:
                return util.returnErrorShorcut(400, 'Project id is not valid')
        except:
            return util.returnErrorShorcut(400, 'Project id is not valid')

        Concepts.objects.filter(project=user_data['id']).update(concepts=user_data['concepts'])
        param_dict['concepts']=user_data['concepts']
        return util.returnSuccessShorcut(param_dict)



#This Class will take a input as a job description and it will retun the output as a concepts(skills)
class Alchemy_api():
    @csrf_exempt

    #This API is analsys a project description and reuturn a concepts
    def analsys(request):
        concepts_obj=Concepts()
        param_dict = {}
        try:
            user_data=json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400,'API parameter is not valid')
        recuriter_email = User.objects.filter(email=user_data['recuriter'])
        if not recuriter_email:
            return util.returnErrorShorcut(404, 'Recuriter email id is not valid')
        values = Token.objects.filter(user=recuriter_email, key=user_data['token'])#.select_related().exists()
        if not values:
            return util.returnErrorShorcut(404, 'Access Token is not valid')
        try:
            project_id = Projects.objects.filter(id=user_data['id'])
            if not project_id:
                return util.returnErrorShorcut(400, 'Project id is not valid')
        except:
            return util.returnErrorShorcut(400, 'Project id is not valid')
        for project_idd in project_id:
            concepts_obj.project=project_idd
            param_dict['project_id'] = str(project_idd)
        try:
            keyword_concepts = Alchemy_api.alchemy_api(user_data)
        except:
            return util.returnErrorShorcut(400,"Description text data is not valid.")
        concepts_obj.concepts = keyword_concepts
        concept_empty=Concepts.objects.filter(project=project_id).values()
        if not concept_empty:
            concepts_obj.save()
            Projects.objects.filter(id=project_id).update(description=user_data['description'])
            param_dict['concepts'] = keyword_concepts
        else:
            try:
                del user_data['token']
                del user_data['recuriter']
            except KeyError:
                pass
            Projects.objects.filter(id=project_id).update(**user_data)
            Concepts.objects.filter(project=project_id).update(concepts=keyword_concepts)
            param_dict['concepts']=keyword_concepts
        return util.returnSuccessShorcut(param_dict)


    def alchemy_api(user_data):
        keyword_list = []
        alchemy_language = AlchemyLanguageV1(api_key=Alchmey_api_key)
        data=json.dumps(
            alchemy_language.entities(
                text=user_data['description']),indent=2)
        d = json.loads(data)
        for list_value in d['entities']:
            if list_value['type']=='JobTitle' or list_value['type']=='Quantity' or list_value['type']=='Person':
                keyword_list.append(list_value['text'])
        return keyword_list

class ProjectList():
    # This API is publishing a project if is_published=true,bu default project list count is 10
    @csrf_exempt
    def publish_project(request):
        output = {'publish_project': []}
        try:
            user_data=json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400,'API parameter is not valid')
        rec_name = User.objects.filter(username=user_data['recuriter'])
        if not rec_name:
            return util.returnErrorShorcut(404, 'Recuriter email id is not valid')
        values = Token.objects.filter(user=rec_name, key=user_data['token'])
        if not values:
            return util.returnErrorShorcut(404, 'Access Token is not valid')
        counter = Projects.objects.filter(is_published=True, recuriter=rec_name).values().order_by('-create_date').count()
        project_list_count={}
        project_list_count['count']=counter
        project = Projects.objects.filter(is_published=True,recuriter=rec_name).values().order_by('-create_date')[:10]
        for project_data in project:
            param_dict = {}
            project_id = Projects.objects.filter(id=project_data['id'])
            for project_idd in project_id:
                param_dict['project_id']=str(project_idd)
            param_dict['project_name']=project_data['project_name']
            user_data=User.objects.filter(id=project_data['recuriter_id']).values('email')
            for email in user_data:
                param_dict['recuriter']=email['email']
            param_dict['location']=project_data['location']
            param_dict['company_name']=project_data['company_name']
            param_dict['create_date']=str(project_data['create_date'].day)+'/'+str(project_data['create_date'].month)+'/'+str(project_data['create_date'].year)
            output['publish_project'].append(param_dict)
        output['publish_project'].append(project_list_count)
        return util.returnSuccessShorcut(output)

    # This API is returning a top 6 project
    @csrf_exempt
    def top_project_list(request):
        output = {'top_project': []}
        try:
            user_data=json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400,'API parameter is not valid')
        rec_name = User.objects.filter(username=user_data['recuriter'])
        if not rec_name:
            return util.returnErrorShorcut(404, 'Recuriter email id is not valid')
        values = Token.objects.filter(user=rec_name, key=user_data['token'])  # .select_related().exists()
        if not values:
            return util.returnErrorShorcut(404, 'Access Token is not valid')
        project = Projects.objects.filter(is_published=True,recuriter=rec_name).values().order_by("-create_date")[:6]
        for project_info in project:
            param_dict = {}
            param_dict['project_name']=project_info['project_name']
            param_dict['location']=project_info['location']
            param_dict['company_name']=project_info['company_name']
            param_dict['create_date']=str(project_info['create_date'].day)+'/'+str(project_info['create_date'].month)+'/'+str(project_info['create_date'].year)
            project_id = Projects.objects.filter(id=project_info['id'])
            for project_idd in project_id:
                concepts_keywords=Concepts.objects.filter(project=project_idd).values('concepts')
                for value in concepts_keywords:
                    concepts=ast.literal_eval(value['concepts'])
                    param_dict['concepts'] = concepts
                    param_dict['project_id']=str(project_idd)
            output['top_project'].append(param_dict)
        return util.returnSuccessShorcut(output)

    ## This API is returning a poject list according the page count
    @csrf_exempt
    def pagination(request):
        output = {'Pagination': []}
        try:
            user_data = json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400, 'API parameter is not valid')
        rec_name = User.objects.filter(username=user_data['recuriter'])
        if not rec_name:
            return util.returnErrorShorcut(404, 'Recuriter email id is not valid')
        values = Token.objects.filter(user=rec_name, key=user_data['token'])  # .select_related().exists()
        if not values:
            return util.returnErrorShorcut(404, 'Access Token is not valid')

        project = Projects.objects.filter(is_published=True, recuriter=rec_name).values().order_by("-create_date")#[:count]

        paginator = Paginator(project,user_data['count'])
        try:
            page = paginator.page(user_data['page'])
        except:
            return util.returnErrorShorcut(404, 'No longer data is available')

        project_data=page.object_list

        for project_data in project_data:
            param_dict = {}
            project_id = Projects.objects.filter(id=project_data['id'])
            for project_idd in project_id:
                param_dict['project_id'] = str(project_idd)
            param_dict['project_name'] = project_data['project_name']
            user_data = User.objects.filter(id=project_data['recuriter_id']).values('email')
            for email in user_data:
                param_dict['recuriter'] = email['email']
            param_dict['location'] = project_data['location']
            param_dict['company_name'] = project_data['company_name']
            param_dict['create_date'] = str(project_data['create_date'].day) + '/' + str(
                project_data['create_date'].month) + '/' + str(project_data['create_date'].year)
            output['Pagination'].append(param_dict)
        return util.returnSuccessShorcut(output)

