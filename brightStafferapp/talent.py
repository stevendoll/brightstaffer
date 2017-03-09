from brightStafferapp.models import Talent, Token, Company, User, Projects, TalentProject, TalentEmail, TalentContact, TalentStage
from brightStafferapp.serializers import TalentSerializer, ProjectSerializer, TalentContactEmailSerializer, TalentProjectStageSerializer
from brightStafferapp import util
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.response import Response
from django.views.generic import View
from rest_framework import generics
import json
from brightStafferapp.util import required_post_params
from brightStafferapp.views import user_validation
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse
from django.db.models import Q
from django.http import QueryDict


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class TalentList(generics.ListCreateAPIView):
    queryset = Talent.objects.all()
    serializer_class = TalentSerializer
    pagination_class = LargeResultsSetPagination
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        result = user_validation(request.query_params)
        if not result:
            return Response({"status": "Fail"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super(TalentList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return Talent.objects.filter(inactive=False, recruiter__username=self.request.query_params['recruiter']) \
            .order_by('-create_date')

    def list(self, request, *args, **kwargs):
        response = super(TalentList, self).list(request, *args, **kwargs)
        user_profile = User.objects.filter(username=self.request.query_params['recruiter'])
        if user_profile:
            user_profile = user_profile[0]
        response.data['display_name'] = user_profile.user_recruiter.display_name
        response.data['talent_list'] = response.data['results']
        response.data['message'] = 'success'
        del (response.data['results'])
        return response


class TalentDetail(generics.RetrieveAPIView):
    queryset = Talent.objects.all()
    model = Talent
    serializer_class = TalentSerializer

    def get_queryset(self):
        queryset = super(TalentDetail, self).get_queryset()
        return queryset


class TalentEmailContactAPI(generics.ListCreateAPIView):
    queryset = Talent.objects.all()
    serializer_class = TalentContactEmailSerializer
    http_method_names = ['get', 'post', 'delete', 'put']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TalentEmailContactAPI, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(TalentEmailContactAPI, self).get_queryset()
        talent_id = self.request.query_params.get('talent_id')
        queryset = queryset.filter(id=talent_id)
        return queryset


class TalentContactAPI(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TalentContactAPI, self).dispatch(request, *args, **kwargs)

    @required_post_params(params=['recruiter', 'token', 'talent_id', 'contact'])
    def post(self, request):
        context = {}
        talent_id = request.POST['talent_id']
        contact = request.POST['contact']
        talent_objs = Talent.objects.filter(id=talent_id)
        if not talent_objs:
            return util.returnErrorShorcut(404, 'Talent with id {} not found'.format(talent_id))
        talent_obj = talent_objs[0]

        if 'updated_contact' in request.POST:
            # request to update the existing email address
            updated_contact = request.POST['updated_contact']
            talent_contact_obj = TalentContact.objects.filter(contact=contact)
            if talent_contact_obj:
                talent_contact_obj = talent_contact_obj[0]
                talent_contact_obj.contact = updated_contact
                talent_contact_obj.save()
                return util.returnSuccessShorcut(context)

        talent_contact_obj, created = TalentContact.objects.get_or_create(talent=talent_obj, contact=contact)
        if created:
            return util.returnSuccessShorcut(context)
        else:
            context['error'] = 'Contact already added for this user'
            return util.returnErrorShorcut(409, context)

    def delete(self, request):
        context = dict()
        contact = request.GET['contact']
        talent_id = request.GET['talent_id']
        talent_objs = Talent.objects.filter(id=talent_id)
        if not talent_objs:
            return util.returnErrorShorcut(404, 'Talent with id {} not found'.format(talent_id))
        talent_obj = talent_objs[0]
        if contact:
            is_deleted = TalentContact.objects.filter(talent=talent_obj, contact=contact).delete()[0]
            if not is_deleted:
                return util.returnErrorShorcut(400, 'No entry found or already deleted')
            return util.returnSuccessShorcut(context)
        else:
            return util.returnErrorShorcut(404, 'Contact not found')


class TalentEmailAPI(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TalentEmailAPI, self).dispatch(request, *args, **kwargs)

    @required_post_params(params=['recruiter', 'token', 'talent_id', 'email'])
    def post(self, request):
        context = {}
        talent_id = request.POST['talent_id']
        email = request.POST['email']
        talent_objs = Talent.objects.filter(id=talent_id)
        if not talent_objs:
            return util.returnErrorShorcut(404, 'Talent with id {} not found'.format(talent_id))
        talent_obj = talent_objs[0]

        if 'updated_email' in request.POST:
            # request to update the existing email address
            updated_email = request.POST['updated_email']
            if_exists = self.validate_email(updated_email)
            if if_exists:
                return util.returnErrorShorcut(409, 'A user is already associated with this email.')
            talent_email_obj = TalentEmail.objects.filter(email=email)
            if talent_email_obj:
                talent_email_obj = talent_email_obj[0]
                talent_email_obj.email = updated_email
                talent_email_obj.save()
                return util.returnSuccessShorcut(context)

        if_exists = self.validate_email(email)
        if if_exists:
            return util.returnErrorShorcut(409, 'A user is already associated with this email.')
        talent_email_obj, created = TalentEmail.objects.get_or_create(talent=talent_obj, email=email)
        if created:
            return util.returnSuccessShorcut(context)
        else:
            context['error'] = 'Email already added for this user'
            return util.returnErrorShorcut(409, context)

    def delete(self, request):
        context = dict()
        talent_obj = None
        email = request.GET['email']
        talent_id = request.GET['talent_id']
        talent_objs = Talent.objects.filter(id=talent_id)
        if not talent_objs:
            return util.returnErrorShorcut(404, 'Talent with id {} not found'.format(talent_id))
        talent_obj = talent_objs[0]
        if email:
            is_deleted = TalentEmail.objects.filter(talent=talent_obj, email=email).delete()[0]
            if not is_deleted:
                return util.returnErrorShorcut(400, 'No entry found or already deleted')
            return util.returnSuccessShorcut(context)
        else:
            return util.returnErrorShorcut(404, 'Email not found')

    def validate_email(self, email):
        users = User.objects.filter(Q(email=email) | Q(username=email))
        if users:
            return True
        else:
            return False


class TalentProjectAddAPI(View):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    http_method_names = ['post']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TalentProjectAddAPI, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = dict()
        project_id = request.POST['project_id']
        recruiter = request.POST['recruiter']
        # get projects instance to verify if project with project_id and recruiter exists or not
        projects = Projects.objects.filter(id=project_id, recruiter__username=recruiter)
        if not projects:
            return util.returnErrorShorcut(403, 'Project with id {} doesn\'t exist in database.'.format(project_id))
        project = projects[0]
        # get list of talent ids from POST request
        talent_id_list = request.POST.getlist('talent_id[]')
        for talent_id in talent_id_list:
            talent_objs = Talent.objects.filter(id=talent_id)
            if not talent_objs:
                return util.returnErrorShorcut(403, 'Talent with id {} doesn\'t exist in database.'.format(talent_id))
            talent_obj = talent_objs[0]
            tp_obj, created = TalentProject.objects.get_or_create(talent=talent_obj, project=project)
            if created:
                context['message'] = 'success'
            else:
                context['error'] = 'Talent Project object already exists.'
                return util.returnErrorShorcut(400, context)
        return util.returnSuccessShorcut(context)


class TalentStageAddAPI(generics.ListCreateAPIView):
    queryset = TalentStage.objects.all()
    serializer_class = TalentProjectStageSerializer
    #pagination_class = LargeResultsSetPagination
    http_method_names = ['get','post']

    # def get(self, request, *args, **kwargs):
    #     result = user_validation(request.query_params)
    #     if not result:
    #         return Response({"status": "Fail"}, status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         return super(TalentStageAddAPI, self).get(request, *args, **kwargs)

    def get(self,request):
        projects = Projects.objects.filter(id=request.GET['project_id'])
        if not projects:
            return util.returnErrorShorcut(403, 'Project with id {} doesn\'t exist in database.'.format(
                request.GET['project_id']))
        project = projects[0]
        talent_objs = Talent.objects.filter(id=request.GET['talent_id'])
        if not talent_objs:
            return util.returnErrorShorcut(404, 'Talent with id {} not found'.format(request.GET['talent_id']))
        talent_obj = talent_objs[0]
        list=TalentStage.objects.filter(id=request.GET['id'], project=project, talent=talent_obj).values()
        return list

    # def list(self, request, *args, **kwargs):
    #     response = super(TalentStageAddAPI, self).list(request, *args, **kwargs)
    #     print (response.data)
    #     #response.data['stage'] = response.data['results']
    #     #response.data['message'] = 'success'
    #     #del (response.data['results'])
    #     return response

    def post(self, request):
        context={}
        talent = request.POST['talent_id']
        project = request.POST['project_id']
        stage = request.POST['stage']
        details = request.POST['details']
        notes = request.POST['notes']
        projects = Projects.objects.filter(id=project)
        if not projects:
            return util.returnErrorShorcut(403, 'Project with id {} doesn\'t exist in database.'.format(project))
        project = projects[0]
        talent_objs = Talent.objects.filter(id=talent)
        if not talent_objs:
            return util.returnErrorShorcut(404, 'Talent with id {} not found'.format(talent))
        talent_obj = talent_objs[0]
        tp_obj, created = TalentStage.objects.get_or_create(talent=talent_obj, project=project, stage=stage, details=details, notes=notes)
        if created:
            context['message'] = 'success'
        return util.returnSuccessShorcut(context)

class TalentUpdateRank(View):

    def get(self,request):
        context={}
        talent = request.GET['talent_id']
        talent_objs = Talent.objects.filter(id=talent)
        if not talent_objs:
            return util.returnErrorShorcut(404, 'Talent with id {} not found'.format(talent))

        updated=Talent.objects.filter(id=talent).update(rating=request.GET['rating'])
        if updated:
            context['message'] = 'success'
        return util.returnSuccessShorcut(context)




def talent_validation(user_data):
    values = Talent.objects.filter(talent_name=user_data['talent'], id=user_data['id'])
    if not values:
        return False
    else:
        return True