import os
import json
import ast
from brightStaffer.settings import concept_relevance
from django.utils import timezone
from watson_developer_cloud import AlchemyLanguageV1
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from brightStafferapp.models import Projects, Concept, ProjectConcept, TalentConcept, PdfImages, FileUpload, Recruiter
from brightStafferapp import util
from brightStafferapp.util import require_post_params
from brightStaffer.settings import Alchemy_api_key
from django.shortcuts import render, HttpResponse
from itertools import chain
from brightStafferapp.serializers import ProjectSerializer, TopProjectSerializer, UserSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.response import Response
from django.views.generic import View
from django.utils.decorators import method_decorator
from uuid import UUID
import PyPDF2
from PIL import Image
import os
import uuid
import textract

class UserData(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UserData, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("405 ERROR:-Method is not allowed")

    def post(self, request):
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


class UserLogin(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UserLogin, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("405 ERROR:-Method is not allowed")

    def post(self, request):
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


class JobPosting(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(JobPosting, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("405 ERROR:-Method is not allowed")

    def post(self, request):
        param_dict = {}
        user_data = json.loads(request.body.decode("utf-8"))
        projects = Projects()
        check_auth = user_validation(user_data)
        if not check_auth:
            return util.returnErrorShorcut(403, 'Either Recruiter Email or Token id is not valid')
        if user_data['id'] == '':
            try:
                rec_name = User.objects.get(username=user_data['recruiter'])
                project_valid = Projects.objects.filter(project_name=user_data['project_name'],
                                                        recruiter=rec_name).exists()
                if not project_valid:
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
            project_id = Projects.objects.filter(id=user_data['id']).exists()
            if not project_id:
                return util.returnErrorShorcut(404, 'Project id is not valid')
            else:
                try:
                    del user_data['token']
                    del user_data['recruiter']
                except KeyError:
                    pass
                Projects.objects.filter(id=user_data['id']).update(**user_data)
                return util.returnSuccessShorcut(param_dict)


# This API is returned a previous page info
class BackButtonInfo(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(BackButtonInfo, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("405 ERROR:-Method is not allowed")

    def post(self, request):
        user_data = json.loads(request.body.decode("utf-8"))
        param_dict = {}
        check_auth = user_validation(user_data)
        if not check_auth:
            return util.returnErrorShorcut(403, 'Either Recruiter Email or Token id is not valid')
        p_check = validate_project_by_id(user_data)
        if not p_check:
            return util.returnErrorShorcut(400, 'Project id is not valid')
        param_dict['project_id'] = user_data['id']
        param_dict['user_token'] = user_data['token']
        param_dict['recruiter'] = user_data['recruiter']
        value = Projects.objects.filter(id=user_data['id']).values()
        for param_value in value:
            if user_data['page'] == 1:
                param_dict['company_name'] = param_value['company_name']
                param_dict['project_name'] = param_value['project_name']
                param_dict['location'] = param_value['location']
            if user_data['page'] == 2:
                param_dict['description'] = param_value['description']
            if user_data['page'] == 3:
                concept_dict = Concept.objects.filter(project=user_data['id']).values('concept')
                for concept_key in concept_dict:
                    param_dict['concept'] = concept_key['concept']
        return util.returnSuccessShorcut(param_dict)


class Publish(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(Publish, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("405 ERROR:-Method is not allowed")

    def post(self, request):
        param_dict = {}
        user_data = json.loads(request.body.decode("utf-8"))
        check_auth = user_validation(user_data)
        if not check_auth:
            return util.returnErrorShorcut(403, 'Either Recruiter Email or Token id is not valid')
        project_id = validate_project_by_id(user_data)
        if not project_id:
            return util.returnErrorShorcut(400, 'Project id is not valid')
        try:
            del user_data['token']
            del user_data['recruiter']
        except KeyError:
            pass
        Projects.objects.filter(id=user_data['id']).update(**user_data)
        Projects.objects.filter(id=user_data['id']).update(create_date=timezone.now())
        return util.returnSuccessShorcut(param_dict)


# This Class will take a input as a job description and it will return the output as a concepts(skills)
class AlchemyAPI(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(AlchemyAPI, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("405 ERROR:-Method is not allowed")

    @require_post_params(params=['recruiter', 'token'])
    def post(self, request):
        """
        This API analyse a project description and return a list of concepts
        :return:
        """
        context = dict()
        user_data = json.loads(request.body.decode("utf-8"))
        check_auth = user_validation(user_data)
        if not check_auth:
            return util.returnErrorShorcut(403, 'Either Recruiter Email or Token id is not valid')
        project_id = validate_project_by_id(user_data)
        if not project_id:
            return util.returnErrorShorcut(400, 'Project id is not valid')

        # call the alchemy api and get list of concepts
        project_obj = Projects.objects.get(id=user_data['id'])
        keyword_concepts = self.alchemy_api(user_data, project_obj.id)
        if keyword_concepts:
            for keyword in keyword_concepts:
                concept, created = Concept.objects.get_or_create(concept=keyword)
                ProjectConcept.objects.get_or_create(project=project_obj, concept=concept)
        else:
            return util.returnErrorShorcut(400, "Description text data is not valid.")
        del user_data['token']
        del user_data['recruiter']
        Projects.objects.filter(id=project_obj.id).update(**user_data)
        context['concept'] = keyword_concepts
        return util.returnSuccessShorcut(context)

    # @staticmethod
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


class UpdateConcepts(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateConcepts, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        param_dict = {}
        try:
            user_data = json.loads(request.body.decode("utf-8"))
        except ValueError:
            return util.returnErrorShorcut(400, 'API parameter is not valid')
        check_auth = user_validation(user_data)
        if not check_auth:
            return util.returnErrorShorcut(403, 'Either Recruiter Email or Token id is not valid')
        project_id = validate_project_by_id(user_data)
        if not project_id:
            return util.returnErrorShorcut(400, 'Project id is not valid')
        project_obj = Projects.objects.get(id=user_data['id'])
        if user_data['concept']:
            create_update_concepts(user_data['concept'], project_obj)
        return util.returnSuccessShorcut(param_dict)


def create_update_concepts(concepts, project_obj):
    project_concepts = []
    if project_obj:
        project_concepts = list(ProjectConcept.objects.filter(project=project_obj).values_list('id', flat=True))
    for keyword in concepts:
        concept, created = Concept.objects.get_or_create(concept=keyword)
        project_concept, proj_created = ProjectConcept.objects.get_or_create(project=project_obj, concept=concept)
        if project_concept.id in project_concepts:
            project_concepts.remove(project_concept.id)
    ProjectConcept.objects.filter(id__in=project_concepts).delete()


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
            return super(ProjectList, self).get(request, *args, **kwargs)

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
            return super(TopProjectList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        rec_name = User.objects.filter(username=self.request.query_params['recruiter'])
        return Projects.objects.filter(is_published=True, recruiter=rec_name).order_by('-create_date')[:6]

    def list(self, request, *args, **kwargs):
        response = super(TopProjectList, self).list(request, *args, **kwargs)
        response.data['top_project'] = response.data['results']
        response.data['message'] = 'success'
        del (response.data['results'])
        return response


class UpdateRecruiter(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateRecruiter, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        param_dict = {}
        recruiter = request.GET['recruiter']
        display_name = request.GET['display_name']
        user = User.objects.filter(username=recruiter)
        if not user:
            return util.returnErrorShorcut(403, 'Recruiter Email is not valid')
        Recruiter.objects.filter(user=user[0]).update(display_name=display_name)
        param_dict['display_name'] = display_name
        return util.returnSuccessShorcut(param_dict)


class FileUploadView(View):
    """
    Handles file uploading by drag and drop feature for add talent functionality.
    """

    FILTER_DICT = {'/FlateDecode': '.png',
                   '/DCTDecode': '.jpg',
                   '/JPXDecode': '.jp2'
                   }

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(FileUploadView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """
        :param request: incoming POST request with files
        :return: success or error response
        """
        try:
            files = request.FILES
            if not files:
                return util.returnErrorShorcut(400, "No files attached with this request")
            user_username = request.POST['recruiter']
            user = User.objects.filter(username=user_username)
            if user:
                user = user[0]
            dest_path = os.path.join(settings.MEDIA_URL, user_username)
            # create destination path if not exists, send this to utils later, since will occur in many scenarios
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            for key, file in files.items():
                file_upload_obj = self.handle_uploaded_file(dest_path, file, user)
                # extract text from pdf
                self.extract_text_from_pdf(file_upload_obj)
                # extract all images from pdf
                self.extract_image_from_pdf(file_upload_obj, dest_path='images')
            context = dict()
            return util.returnSuccessShorcut(context)
        except:
            return util.returnErrorShorcut(400, "Error Connection Refused")

    # @staticmethod
    def handle_uploaded_file(self, dest_path, f, user):
        """
        :param dest_path: destination path for the file currently being saved
        :param f: InMemoryUploadedFile object from request.FILES
        :param user: user uploading the file
        :return: <FileUpload object> or error
        """
        try:
            file_name = str(uuid.uuid4())
            file_upload_obj = FileUpload.objects.create(name=file_name, file=f, user=user)
            return file_upload_obj
        except Exception as e:
            print(e)
            return util.returnErrorShorcut(400, "Error Connection Refused")

    def extract_image_from_pdf(self, file_upload_obj, dest_path=None):
        """
        :param file_upload_obj: model object of the newly uploaded file. This object is already saved in database
        and is now sent to extract images from the pdf file
        :param dest_path: destination path for extracted images
        :return: None or error
        """
        input1 = PyPDF2.PdfFileReader(open(file_upload_obj.file.path, "rb"))
        page0 = input1.getPage(0)
        dest_path = os.path.join("/".join(file_upload_obj.file.path.split('/')[:-1]), dest_path)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        # check if /XObject is present in page. This object checks if there is any image present in pdf file.
        if '/XObject' not in page0['/Resources']:
            return
        xobject = page0['/Resources']['/XObject'].getObject()
        for obj in xobject:
            if xobject[obj]['/Subtype'] == '/Image':
                size = (xobject[obj]['/Width'], xobject[obj]['/Height'])
                data = xobject[obj].getData()
                unique_name = str(uuid.uuid4())
                img_obj = PdfImages()
                img_obj.file = file_upload_obj
                img_obj.name = unique_name
                img_obj.save()
                if xobject[obj]['/ColorSpace'] == '/DeviceRGB':
                    mode = "RGB"
                else:
                    mode = "P"

                img_name = os.path.join(dest_path, unique_name)

                # /FlateDecode for .png
                if xobject[obj]['/Filter'] == '/FlateDecode':
                    img = Image.frombytes(mode, size, data)
                    img_name += self.FILTER_DICT[xobject[obj]['/Filter']]
                    img.save(img_name)
                    img_obj.image = img_name
                elif xobject[obj]['/Filter'] == '/DCTDecode':
                    img_name += self.FILTER_DICT[xobject[obj]['/Filter']]
                    img = open(img_name, "wb+")
                    img.write(data)
                    img_obj.image = img_name
                    img.close()
                elif xobject[obj]['/Filter'] == '/JPXDecode':
                    img_name += self.FILTER_DICT[xobject[obj]['/Filter']]
                    img = open(img_name, "wb")
                    img.write(data)
                    img_obj.image = img_name
                    img.close()
                img_obj.save()

    def extract_text_from_pdf(self, file_upload_obj):
        """
        :param file_upload_obj: model object of the newly uploaded file. This object is already saved in database
        and is now sent to extract text from the pdf file
        :return: None or error
        """
        text = textract.process(file_upload_obj.file.path)
        file_upload_obj.text = text
        file_upload_obj.save()


def user_validation(data):
    values = Token.objects.filter(user__username=data['recruiter'], key=data['token'])
    if not values:
        return False
    else:
        return True


def validate_project_by_id(request_data):
    try:
        UUID(request_data['id'], version=4)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return False
    p_id = Projects.objects.filter(id=request_data['id'])
    if not p_id:
        return False
        # If it's a value error, then the string
        # is not a valid project id.
    else:
        # Return True if the project id is valid
        return True