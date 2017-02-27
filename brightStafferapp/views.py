import os
import json
from brightStaffer.settings import concept_relevance
from django.utils import timezone
from watson_developer_cloud import AlchemyLanguageV1
from django.conf import settings
from django.contrib.auth import authenticate
# from django.contrib.auth.models import User
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from brightStafferapp.models import Projects,Concept
from brightStafferapp import util
from brightStafferapp.util import require_post_params
from brightStaffer.settings import Alchemy_api_key
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
import ast
from itertools import chain
# from collections import OrderedDict
from brightStafferapp.serializers import ProjectSerializer, TopProjectSerializer, UserSerializer
from rest_framework import generics
from django.contrib.auth.models import User
# from rest_framework import permissions
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework.reverse import reverse
# from rest_framework import renderer
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
# from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.generic import View
from django.utils.decorators import method_decorator


class UserData(generics.ListCreateAPIView):
    queryset = Projects.objects.all()
    serializer_class = UserSerializer
    # SignupAPI
    @api_view(['POST'])
    def user_account(request):
        param_dict = {}
        profile_data = json.loads(request.body.decode("utf-8"))
        try:
            User.objects.create_user(first_name=profile_data['firstName'], last_name=profile_data['lastName'],
                                     email=profile_data['userEmail'], password=profile_data['password'],
                                     username=profile_data['userEmail'])
            user = authenticate(username=profile_data['userEmail'], password=profile_data["password"])
            token = Token.objects.get(user=user)
            param_dict['first_name'] = profile_data['firstName']
            param_dict['last_name'] = profile_data['lastName']
            param_dict['user_name'] = profile_data["userEmail"]
            param_dict['user_token'] = token.key
        except IntegrityError:
            return util.returnErrorShorcut(404, 'Email id is already exist')
        return util.returnSuccessShorcut(param_dict)


    # Login API
    @csrf_exempt
    def user_login(request):
        param_dict = {}
        try:
            user_data = json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400, 'Invalid Form Fields')
        user = authenticate(username=user_data["username"], password=user_data["password"])
        try:
            user_profile = User.objects.all().values('first_name', 'last_name').filter(username=user)
            list_result = [entry for entry in user_profile]
            result_set = list_result[0]
            token = Token.objects.get(user=user)
            param_dict['user_name'] = user_data["username"]
            param_dict['user_token'] = token.key
            param_dict['first_name'] = result_set['first_name']
            param_dict['last_name'] = result_set['last_name']
        except:
            return util.returnErrorShorcut(401, 'UnAuthorized User')
        return util.returnSuccessShorcut(param_dict)

    def home(request):
        return render(request, 'index.html', {'STATIC_URL': settings.STATIC_URL})


class JobPosting():
    @csrf_exempt
    def job_posting(request):
        param_dict = {}
        try:
            user_data = json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400, 'API parameter is not valid')
        recruiter_email = User.objects.filter(email=user_data['recruiter'])
        recruiter_email_valid = User.objects.filter(email=user_data['recruiter']).exists()
        projects = Projects()
        if recruiter_email_valid == False:
            return util.returnErrorShorcut(404, 'Recruiter email id is not valid')
        values = Token.objects.filter(user=recruiter_email, key=user_data['token']).select_related().exists()
        if values == False:
            return util.returnErrorShorcut(404, 'Access Token is not valid')
        else:
            if user_data['id'] == '':
                try:
                    rec_name = User.objects.get(username=user_data['recruiter'])
                    pname_valid = Projects.objects.filter(project_name=user_data['project_name'],recruiter=rec_name).exists()
                    if pname_valid == False:
                        projects.project_name = user_data['project_name']
                        projects.recruiter = rec_name
                        projects.is_published = user_data['is_published']
                        projects.save()
                        p_id = Projects.objects.filter(project_name=user_data['project_name'],
                                                       recruiter=rec_name).values('id')
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
                            del user_data['recruiter']
                        except KeyError:
                            pass
                        Projects.objects.filter(id=user_data['id']).update(**user_data)
                        return util.returnSuccessShorcut(param_dict)
                except:
                    return util.returnErrorShorcut(400, 'API parameter is not valid')

    # This API is returned a previous page info
    @csrf_exempt
    def backButtonInfo(request):
        param_dict = {}
        try:
            user_data = json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400, 'API parameter is not valid')
        recuriter_email = User.objects.filter(email=user_data['recruiter'])
        if not recuriter_email:
            return util.returnErrorShorcut(404, 'Recruiter email id is not valid')
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
        param_dict['recruiter'] = user_data['recruiter']
        value = Projects.objects.filter(id=user_data['id']).values()
        for param_value in value:
            if user_data['page'] == 1:
                param_dict['company_name']=param_value['company_name']
                param_dict['project_name']=param_value['project_name']
                param_dict['location']=param_value['location']
            if user_data['page'] == 2:
                param_dict['description']=param_value['description']
            if user_data['page'] == 3:
                concept_dict = Concept.objects.filter(project=user_data['id']).values('concept')
                for concept_key in concept_dict:
                    param_dict['concept'] = concept_key['concept']

        return util.returnSuccessShorcut(param_dict)

    # This API is publish a project
    @csrf_exempt
    def publish(request):
        param_dict = {}
        try:
            user_data = json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400, 'API parameter is not valid')
        recuriter_email = User.objects.filter(email=user_data['recruiter'])
        if not recuriter_email:
            return util.returnErrorShorcut(404, 'Recruiter email id is not valid')
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
            del user_data['recruiter']
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
        validate_email_and_token(user_data)
        project_id = validate_project_by_id(user_data)
        concept_obj, created = Concept.objects.get_or_create(project_id=project_id)
        concept_obj.concept = user_data['concept']
        concept_obj.save()
        param_dict['concept'] = concept_obj.concept
        return util.returnSuccessShorcut(param_dict)


def validate_project_by_id(request_data):
    try:
        project_id = Projects.objects.get(id=request_data['id'])
        if not project_id:
            return util.returnErrorShorcut(400, 'Project id is not valid')
        return project_id
    except:
        return util.returnErrorShorcut(400, 'Project id is not valid')


def validate_email_and_token(request_data):
    recruiter_email = User.objects.filter(email=request_data['recruiter'])
    if not recruiter_email:
        return util.returnErrorShorcut(404, 'Recruiter email id is not valid')
    values = Token.objects.filter(user=recruiter_email, key=request_data['token'])  # .select_related().exists()
    if not values:
        return util.returnErrorShorcut(404, 'Access Token is not valid')


# This Class will take a input as a job description and it will return the output as a concepts(skills)
class AlchemyAPI(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(AlchemyAPI, self).dispatch(request, *args, **kwargs)

    @require_post_params(params=['recruiter', 'token'])
    def post(self, request):
        """
        This API analyse a project description and return a list of concepts
        :return:
        """
        context = dict()
        concept_obj = None
        try:
            user_data = json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400, 'API parameter is not valid')
        validate_email_and_token(user_data)
        project_id = validate_project_by_id(user_data)

        if project_id:
            project_id = str(project_id)
            concept_obj, created = Concept.objects.get_or_create(project_id=project_id)
            Projects.objects.filter(id=project_id).update(description=user_data['description'])
            context['project_id'] = str(project_id)

        # call the alchemy api and get list of concepts
        keyword_concepts = self.alchemy_api(user_data, project_id)
        if keyword_concepts:
            concept_obj.concept = keyword_concepts
            concept_obj.save()
        else:
            return util.returnErrorShorcut(400, "Description text data is not valid.")
        del user_data['token']
        del user_data['recruiter']
        Projects.objects.filter(id=project_id).update(**user_data)
        concept_obj.concept = keyword_concepts
        context['concept'] = keyword_concepts
        return util.returnSuccessShorcut(context)

    def alchemy_api(self, user_data, project_id):
        keyword_list = []
        try:
            alchemy_language = AlchemyLanguageV1(api_key=Alchemy_api_key)
            data = json.dumps(
                alchemy_language.combined(text=user_data['description'],
                                          extract='entities,keywords', max_items=25))
            d = json.loads(data)
            Projects.objects.filter(id=project_id).update(description_analysis=d)
            for item in chain(d["keywords"], d["entities"]):
                if round(float(item['relevance']), 2) >= concept_relevance:
                    keyword_list.append(item['text'].lower())
            return list(set(keyword_list))[:25]
        except Exception as e:
            return keyword_list


class LargeResultsSetPagination(PageNumberPagination):
    page_size =10
    page_size_query_param = 'page_size'
    max_page_size = 10


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ProjectList(generics.ListCreateAPIView):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = LargeResultsSetPagination
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        result = user_validation(request.query_params)
        if not result:
            return Response({"status": "Fail"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super(ProjectList, self).get(request, *args, *kwargs)

    def get_queryset(self):
        count = self.request.query_params['count']
        self.pagination_class.page_size = count
        return Projects.objects.filter(is_published=True, recruiter__username=self.request.query_params['recruiter'])\
            .order_by('-create_date')

    def list(self, request, *args, **kwargs):
        response = super(ProjectList, self).list(request, *args, **kwargs)
        response.data['published_projects'] = response.data['results']
        response.data['message'] = 'success'
        del (response.data['results'])
        return response


class TopProjectList(generics.ListCreateAPIView):
    queryset = Projects.objects.all()
    serializer_class = TopProjectSerializer
    pagination_class = LargeResultsSetPagination
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        result = user_validation(request.query_params)
        if not result:
            return Response({"status": "Fail"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super(TopProjectList, self).get(request, *args, *kwargs)

    def get_queryset(self):
        rec_name = User.objects.filter(username=self.request.query_params['recruiter'])
        return Projects.objects.filter(is_published=True, recruiter=rec_name).order_by('-create_date')[:6]

    def list(self, request, *args, **kwargs):
        response = super(TopProjectList, self).list(request, *args, **kwargs)
        for result in response.data['results']:
            if len(result['concepts'])>0:
                result['concepts'] = result['concepts'][0]
                concept = ast.literal_eval(result['concepts'])
                result['concepts'] = concept
            else:
                result['concepts']=result['concepts']
        response.data['top_project'] = response.data['results']
        response.data['message'] = 'success'
        del (response.data['results'])
        return response


def user_validation(data):
    values = Token.objects.filter(user__username=data['recruiter'], key=data['token'])
    if not values:
        return False
    else:
        return True


class FileUpload(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FileUpload, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        #print (request.body.datya)
        files = request.FILES.getlist('file')
        dest_path = settings.MEDIA_URL
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        for file in files:
            self.handle_uploaded_file(dest_path, file)
        context = dict()
        return util.returnSuccessShorcut(context)

    def handle_uploaded_file(self, dest_path, f):
        file_obj = open(dest_path + f.name, 'wb+')
        for chunk in f.chunks():
            file_obj.write(chunk)
            file_obj.close()


