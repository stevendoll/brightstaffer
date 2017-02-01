import json
from brightStaffer.settings import concept_relevance
from django.utils import timezone
from watson_developer_cloud import AlchemyLanguageV1
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from brightStafferapp.models import Projects,Concept
from brightStafferapp import util
from brightStaffer.settings import Alchemy_api_key
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
import ast
from itertools import chain
from collections import OrderedDict
from brightStafferapp.serializers import ProjectSerializer, UserSerializer, ConceptSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


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
        recuriter_email = User.objects.filter(email=user_data['recruiter'])
        recuriter_email_valid=User.objects.filter(email=user_data['recruiter']).exists()
        projects=Projects()
        if recuriter_email_valid == False:
            return util.returnErrorShorcut(404, 'Recruiter email id is not valid')
        values = Token.objects.filter(user=recuriter_email,key=user_data['token']).select_related().exists()
        if values == False:
            return util.returnErrorShorcut(404, 'Access Token is not valid')
        else:
            if user_data['id']=='':
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
            if user_data['page']==1:
                param_dict['company_name']=param_value['company_name']
                param_dict['project_name']=param_value['project_name']
                param_dict['location']=param_value['location']
            if user_data['page']==2:
                param_dict['description']=param_value['description']
            if user_data['page']==3:
                concept_dict=Concept.objects.filter(project=user_data['id']).values('concept')
                for concept_key in concept_dict:
                    param_dict['concept']=concept_key['concept']

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

        Concept.objects.filter(project=user_data['id']).update(concept=user_data['concept'])
        param_dict['concept']=user_data['concept']
        return util.returnSuccessShorcut(param_dict)


# This Class will take a input as a job description and it will retun the output as a concepts(skills)
class Alchemy_api():

    @csrf_exempt
    # This API is analsys a project description and reuturn a concepts
    def analsys(request):
        concepts_obj=Concept()
        param_dict = {}
        try:
            user_data=json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400,'API parameter is not valid')
        recuriter_email = User.objects.filter(email=user_data['recruiter'])
        if not recuriter_email:
            return util.returnErrorShorcut(404, 'Recruiter email id is not valid')
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
            keyword_concepts = Alchemy_api.alchemy_api(user_data,project_id)
        except:
            return util.returnErrorShorcut(400,"Description text data is not valid.")
        concepts_obj.concept = keyword_concepts
        concept_empty=Concept.objects.filter(project=project_id).values()
        if not concept_empty:
            concepts_obj.save()
            Projects.objects.filter(id=project_id).update(description=user_data['description'])
            param_dict['concept'] = keyword_concepts
        else:
            try:
                del user_data['token']
                del user_data['recruiter']
            except KeyError:
                pass
            Projects.objects.filter(id=project_id).update(**user_data)
            Concept.objects.filter(project=project_id).update(concept=keyword_concepts)
            param_dict['concept']=keyword_concepts
        return util.returnSuccessShorcut(param_dict)

    def alchemy_api(user_data,project_id):
        keyword_list = []
        alchemy_language = AlchemyLanguageV1(api_key=Alchemy_api_key)
        data = json.dumps(
            alchemy_language.combined(
                text=user_data['description'],
                extract='entities,keywords',max_items=25))
        d = json.loads(data)
        Projects.objects.filter(id=project_id).update(description_analysis=d)
        for item in chain(d["keywords"], d["entities"]):
            if round(float(item['relevance']),2)>=concept_relevance:
                keyword_list.append(item['text'].lower())
        return list(set(keyword_list))[:25]


class LargeResultsSetPagination(PageNumberPagination):
    page_size =10
    page_size_query_param = 'page_size'
    max_page_size = 10


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class TopProjectList(generics.ListCreateAPIView):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = LargeResultsSetPagination
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        result = user_validation(request.query_params)
        if not result:
            return Response({"status": "Fail"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super(TopProjectList, self).get(request, *args, *kwargs)

    def get_queryset(self):
        count = self.request.query_params['count']
        self.pagination_class.page_size = count
        rec_name = User.objects.filter(username=self.request.query_params['recruiter'])
        return Projects.objects.filter(is_published=True, recruiter=rec_name).order_by('-create_date')

    # def paginate_queryset(self, queryset):
    #     queryset = super(TopProjectList, self).paginate_queryset(queryset)
    #     count = int(self.request.query_params['count'])
    #     self.pagination_class.page_size = count
    #     return queryset

    def list(self, request, *args, **kwargs):
        response = super(TopProjectList, self).list(request, *args, **kwargs)
        response.data['published_projects'] = response.data['results']
        response.data['message'] = 'success'
        del (response.data['results'])
        return response


def user_validation(data):
    values = Token.objects.filter(user__username=data['recruiter'], key=data['token'])
    if not values:
        return False
    else:
        return True

# class TopPublishedProjects(generics.ListCreateAPIView):
#     queryset = Projects.objects.all()
#     serializer_class = ProjectSerializer
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
#     pagination_class = LargeResultsSetPagination
#
#     def get_queryset(self):
#         return Projects.objects.filter(is_published=True).order_by('-create_date')[:10]
#
# class UserList(generics.ListAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
# class UserDetail(generics.RetrieveAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ProjectList():
    # This API is publishing a project if is_published=true,by default project list count is 10
    # @csrf_exempt
    # def publish_project(request):
    #     output = {'publish_project': []}
    #     try:
    #         user_data=json.loads(request.body.decode("utf-8"))
    #     except ValueError:
    #         return util.returnErrorShorcut(400,'API parameter is not valid')
    #     rec_name = User.objects.filter(username=user_data['recruiter'])
    #     if not rec_name:
    #         return util.returnErrorShorcut(404, 'Recruiter email id is not valid')
    #     values = Token.objects.filter(user=rec_name, key=user_data['token'])
    #     if not values:
    #         return util.returnErrorShorcut(404, 'Access Token is not valid')
    #     counter = Projects.objects.filter(is_published=True, recruiter=rec_name).values().order_by('-create_date').count()
    #     project_list_count={}
    #     project_list_count['count']=counter
    #     project = Projects.objects.filter(is_published=True,recruiter=rec_name).values().order_by('-create_date')[:10]
    #     for project_data in project:
    #         param_dict = {}
    #         project_id = Projects.objects.filter(id=project_data['id'])
    #         for project_idd in project_id:
    #             param_dict['project_id']=str(project_idd)
    #         param_dict['project_name']=project_data['project_name']
    #         user_data=User.objects.filter(id=project_data['recruiter_id']).values('email')
    #         for email in user_data:
    #             param_dict['recruiter']=email['email']
    #         param_dict['location']=project_data['location']
    #         param_dict['company_name']=project_data['company_name']
    #         param_dict['create_date']=str(project_data['create_date'].day)+'/'+str(project_data['create_date'].month)+'/'+str(project_data['create_date'].year)
    #         output['publish_project'].append(param_dict)
    #     output['publish_project'].append(project_list_count)
    #     return util.returnSuccessShorcut(output)

    # This API is returning a top 6 project
    @csrf_exempt
    def top_project_list(request):
        output = {'top_project': []}
        try:
            user_data=json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400,'API parameter is not valid')
        rec_name = User.objects.filter(username=user_data['recruiter'])
        if not rec_name:
            return util.returnErrorShorcut(404, 'Recruiter email id is not valid')
        values = Token.objects.filter(user=rec_name, key=user_data['token'])  # .select_related().exists()
        if not values:
            return util.returnErrorShorcut(404, 'Access Token is not valid')
        project = Projects.objects.filter(is_published=True,recruiter=rec_name).values().order_by("-create_date")[:6]
        for project_info in project:
            param_dict = {}
            param_dict['project_name']=project_info['project_name']
            param_dict['location']=project_info['location']
            param_dict['company_name']=project_info['company_name']
            param_dict['create_date']=str(project_info['create_date'].day)+'/'+str(project_info['create_date'].month)+'/'+str(project_info['create_date'].year)
            project_id = Projects.objects.filter(id=project_info['id'])
            for project_idd in project_id:
                concepts_keywords=Concept.objects.filter(project=project_idd).values('concept')
                for value in concepts_keywords:
                    concept=ast.literal_eval(value['concept'])
                    param_dict['concept'] = concept
                    param_dict['project_id']=str(project_idd)
            output['top_project'].append(param_dict)
        return util.returnSuccessShorcut(output)

    # This API is returning a poject list according the page count
    @csrf_exempt
    def pagination(request):
        output = {'Pagination': []}
        try:
            user_data = json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400, 'API parameter is not valid')
        rec_name = User.objects.filter(username=user_data['recruiter'])
        if not rec_name:
            return util.returnErrorShorcut(404, 'Recruiter email id is not valid')
        values = Token.objects.filter(user=rec_name, key=user_data['token'])  # .select_related().exists()
        if not values:
            return util.returnErrorShorcut(404, 'Access Token is not valid')

        project = Projects.objects.filter(is_published=True, recruiter=rec_name).values().order_by("-create_date")#[:count]

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
            user_data = User.objects.filter(id=project_data['recruiter_id']).values('email')
            for email in user_data:
                param_dict['recruiter'] = email['email']
            param_dict['location'] = project_data['location']
            param_dict['company_name'] = project_data['company_name']
            param_dict['create_date'] = str(project_data['create_date'].day) + '/' + str(
                project_data['create_date'].month) + '/' + str(project_data['create_date'].year)
            output['Pagination'].append(param_dict)
        return util.returnSuccessShorcut(output)