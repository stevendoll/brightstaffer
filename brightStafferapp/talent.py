from brightStafferapp.models import Talent, User, Projects, TalentProject, TalentEmail, TalentContact, \
    TalentStage, TalentRecruiter, TalentConcept, ProjectConcept,Concept, Education, TalentEducation, Company,\
    TalentCompany, TalentLocation
from brightStafferapp.serializers import TalentSerializer, TalentContactEmailSerializer, TalentProjectStageSerializer, \
    TalentStageSerializer
from brightStafferapp import util
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
import json
import re
from brightStafferapp.util import required_post_params, required_get_params, required_headers
from brightStafferapp.views import user_validation
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse
from django.db.models import Q
from elasticsearch import Elasticsearch
from datetime import datetime
from .search import TERM_QUERY, BASE_QUERY, EMPTY_QUERY
from django.conf import settings
import copy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import math
import datetime
from datetime import date
from brightStafferapp.google_custom_search import GoogleCustomSearch
from django.utils import timezone


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'count'
    max_page_size = 100


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'count'
    max_page_size = 1000


class TalentList(generics.ListCreateAPIView):
    queryset = Talent.objects.all()
    serializer_class = TalentSerializer
    pagination_class = LargeResultsSetPagination
    http_method_names = ['get']

    @required_get_params(params=['recruiter', 'token', 'count'])
    def get(self, request, *args, **kwargs):
        result = user_validation(request.query_params)
        if not result:
            return Response({"status": "Fail"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super(TalentList, self).get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(TalentList, self).get_queryset()
        context = super(TalentList, self).get_serializer_context()
        recruiter = context['request'].GET.get('recruiter', '')
        if recruiter:
            queryset = queryset.filter(Q(recruiter__username=recruiter) &
                                       Q(talent_active__is_active=True)).order_by('-create_date')
        return queryset

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


# Show Talent Profile API
class TalentDetail(generics.RetrieveAPIView):
    queryset = Talent.objects.all()
    model = Talent
    serializer_class = TalentSerializer

    def get_queryset(self):
        queryset = super(TalentDetail, self).get_queryset()
        return queryset


# Show Talent Email and Contact API
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


# Show Talent Contact API
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
            return util.returnErrorShorcut(400, 'Talent with id {} not found'.format(talent_id))
        talent_obj = talent_objs[0]

        if 'updated_contact' in request.POST:
            # request to update the existing email address
            updated_contact = request.POST['updated_contact']
            if_exists = self.validate_contact(updated_contact)
            if if_exists:
                context['success'] = False
                return util.returnErrorShorcut(409, 'Contact is already exist in the System.')
            talent_contact_obj = TalentContact.objects.filter(contact=contact)
            if talent_contact_obj:
                talent_contact_obj = talent_contact_obj[0]
                talent_contact_obj.contact = updated_contact
                talent_contact_obj.save()
                context['success'] = True
                return util.returnSuccessShorcut(context)

        if_exists = self.validate_contact(contact)
        if if_exists:
            return util.returnErrorShorcut(409, 'Contact is already exist in the System.')
        talent_contact_obj, created = TalentContact.objects.get_or_create(talent=talent_obj, contact=contact)
        if created:
            context['success'] = True
            return util.returnSuccessShorcut(context)
        else:
            context['success'] = False
            context['error'] = 'Contact is already exist in the System.'
            return util.returnErrorShorcut(409, context)

    def delete(self, request):
        context = dict()
        contact = request.GET['contact']
        talent_id = request.GET['talent_id']
        talent_objs = Talent.objects.filter(id=talent_id)
        if not talent_objs:
            context['success'] = False
            return util.returnErrorShorcut(400, 'Talent with id {} not found'.format(talent_id))
        talent_obj = talent_objs[0]
        if contact:
            is_deleted = TalentContact.objects.filter(talent=talent_obj, contact=contact).delete()[0]
            if not is_deleted:
                context['success'] = False
                return util.returnErrorShorcut(400, 'No entry found or already deleted')
            context['success'] = True
            return util.returnSuccessShorcut(context)
        else:
            context['success'] = False
            return util.returnErrorShorcut(400, 'Contact not found')

    def validate_contact(self,contact):
        users = TalentContact.objects.filter(contact=contact,talent__talent_active__is_active=True)
        if users:
            return True
        else:
            return False


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
            context['success'] = False
            return util.returnErrorShorcut(400, 'Talent with id {} not found'.format(talent_id))
        talent_obj = talent_objs[0]

        if 'updated_email' in request.POST:
            # request to update the existing email address
            updated_email = request.POST['updated_email']
            if_exists = self.validate_email(updated_email)
            if if_exists:
                context['success'] = False
                return util.returnErrorShorcut(409, 'Email is already exist in the System.')
            talent_email_obj = TalentEmail.objects.filter(email=email)
            if talent_email_obj:
                talent_email_obj = talent_email_obj[0]
                talent_email_obj.email = updated_email
                talent_email_obj.save()
                context['success'] = True
                return util.returnSuccessShorcut(context)

        if_exists = self.validate_email(email)
        if if_exists:
            context['success'] = False
            return util.returnErrorShorcut(409, 'Email is already exist in the System.')
        talent_email_obj, created = TalentEmail.objects.get_or_create(talent=talent_obj, email=email)
        if created:
            context['success'] = True
            return util.returnSuccessShorcut(context)
        else:
            context['success'] = False
            context['error'] = 'Email is already exist in the System.'
            return util.returnErrorShorcut(409, context)

    def delete(self, request):
        context = dict()
        email = request.GET['email']
        talent_id = request.GET['talent_id']
        talent_objs = Talent.objects.filter(id=talent_id)
        if not talent_objs:
            context['success'] = False
            return util.returnErrorShorcut(400, 'Talent with id {} not found'.format(talent_id))
        talent_obj = talent_objs[0]
        if email:
            is_deleted = TalentEmail.objects.filter(talent=talent_obj, email=email).delete()[0]
            if not is_deleted:
                context['success'] = False
                return util.returnErrorShorcut(400, 'No entry found or already deleted')
            context['success'] = True
            return util.returnSuccessShorcut(context)
        else:
            context['success'] = False
            return util.returnErrorShorcut(400, 'Email not found')

    def validate_email(self, email):
        users = TalentEmail.objects.filter(email=email,talent__talent_active__is_active=True)
        if users:
            return True
        else:
            return False


class TalentProjectAddAPI(generics.ListCreateAPIView):
    queryset = Talent.objects.all()
    serializer_class = TalentSerializer
    http_method_names = ['get']

    def get_queryset(self):
        queryset = super(TalentProjectAddAPI, self).get_queryset()
        talent_result = None
        project_id = self.request.query_params.get('project_id')
        recruiter = self.request.query_params.get('recruiter')
        # get projects instance to verify if project with project_id and recruiter exists or not
        projects = Projects.objects.filter(id=project_id, recruiter__username=recruiter)
        if not projects:
            return util.returnErrorShorcut(400, 'Project with id {} doesn\'t exist in database.'.format(project_id))
        project = projects[0]
        # get list of talent ids from POST request
        talent_id_list = self.request.query_params.get('talent_id[]').split(',')
        for talent_id in talent_id_list:
            talent_objs = Talent.objects.filter(id=talent_id)
            if not talent_objs:
                return util.returnErrorShorcut(400, 'Talent with id {} doesn\'t exist in database.'.format(talent_id))
            talent_obj = talent_objs[0]
            tp_obj, created = TalentProject.objects.get_or_create(talent=talent_obj, project=project)
            #Talent.objects.filter(id=talent_id).update(activation_date=timezone.now())
            talent_result = queryset.filter(talent_active__is_active=True)
            talent_project_match(talent_obj,project)
        return talent_result


def talent_project_match(talent_obj,project):
    talent_concept_list=TalentConcept.objects.filter(talent_id=talent_obj).values_list('concept__concept',flat=True)
    talent_concept_count=TalentConcept.objects.filter(talent_id=talent_obj).values_list('concept__concept',flat=True).count()
    project_concept_list=ProjectConcept.objects.filter(project=project).values_list('concept__concept',flat=True)
    project_concept_count=ProjectConcept.objects.filter(project=project).values_list('concept__concept',flat=True).count()
    total_concept=talent_concept_count+project_concept_count
    count = 0
    if talent_concept_count<=project_concept_count:
        for t_concept in talent_concept_list:
            for p_conecpt in project_concept_list:
                ratio = fuzz.partial_ratio(t_concept.lower(), p_conecpt.lower())
                if ratio >= 90:
                    count += 1
        # match = math.ceil(round((count/project_concept_count), 2))
        match = round(count / project_concept_count * 100)
        if match >= 100:
            match = 100
            TalentProject.objects.filter(talent=talent_obj, project=project).update(project_match=match)
        else:
            TalentProject.objects.filter(talent=talent_obj, project=project).update(project_match=match)
    else:
        for t_concept in talent_concept_list:
            for p_conecpt in project_concept_list:
                ratio = fuzz.partial_ratio(t_concept.lower(), p_conecpt.lower() )
                if ratio >= 90:
                    count += 1
        # match = math.ceil(round((count/project_concept_count), 2))
        match = round(count / talent_concept_count * 100)
        if match >= 100:
            match = 100
            TalentProject.objects.filter(talent=talent_obj, project=project).update(project_match=match)
        else:
            TalentProject.objects.filter(talent=talent_obj, project=project).update(project_match=match)


# View Talent's Current stage for a single project and Add Talent's stage for a single project
class TalentStageAddAPI(generics.ListCreateAPIView):
    queryset = TalentStage.objects.all()
    serializer_class = TalentProjectStageSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        queryset = super(TalentStageAddAPI, self).get_queryset()
        talent_id = self.request.query_params.get('talent_id')
        project_id = self.request.query_params.get('project_id')
        stage_id = self.request.query_params.get('stage_id')
        Talent.objects.filter(id=talent_id).update(activation_date=timezone.now())
        queryset = queryset.filter(id=stage_id, talent_id=talent_id, project_id=project_id)
        return queryset

    def post(self, request, *args, **kwargs):
        context = {}
        talent = request.POST['talent_id']
        project = request.POST['project_id']
        stage = request.POST['stage']
        details = request.POST['details']
        notes = request.POST['notes']
        date = request.POST['date']
        date = datetime.datetime.strptime(date, "%d/%m/%Y")
        projects = Projects.objects.filter(id=project)
        if not projects:
            return util.returnErrorShorcut(400, 'Project with id {} doesn\'t exist in database.'.format(project))
        project = projects[0]
        talent_objs = Talent.objects.filter(id=talent)
        if not talent_objs:
            return util.returnErrorShorcut(400, 'Talent with id {} not found'.format(talent))
        talent_obj = talent_objs[0]
        Talent.objects.filter(id=talent).update(activation_date=timezone.now())
        tp_obj, created = TalentStage.objects.get_or_create(talent=talent_obj, project=project, stage=stage,
                                                            details=details, notes=notes, date_created=date)
        if created:
            queryset = super(TalentStageAddAPI, self).get_queryset()
            queryset = queryset.filter(talent_id=talent)
            # context['talent_id']=tp_obj.talent.talent_name
            # context['stage_id']=tp_obj.id
            # context['project']=tp_obj.project.project_name
            # context['stage']=tp_obj.stage
            # context['details'] = tp_obj.details
            # context['notes'] = tp_obj.notes
            # context['create_date'] = tp_obj.get_date_created
            serializer_data = TalentSerializer(talent_obj)
            context['result'] = serializer_data.data
            return util.returnSuccessShorcut(context)
        else:
            return util.returnErrorShorcut(400, 'Talent stage and info is exist in database, '
                                                'Please create different stage')


# Edit Talent's Stage
class TalentStageEditAPI(generics.ListCreateAPIView):
    queryset = TalentStage.objects.all()
    serializer_class = TalentProjectStageSerializer
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        context = {}
        profile_data = json.loads(request.body.decode("utf-8"))
        recruiter = request.META.get('HTTP_RECRUITER' '')

        token = request.META.get('HTTP_TOKEN' '')
        is_valid = user_validation(data={'recruiter': recruiter,
                                         'token': token})
        if not is_valid:
            return util.returnErrorShorcut(403, 'Either Recruiter Email or Token id is not valid')
        talent = profile_data['talent_id']
        # project = request.POST['project_id']
        stage = profile_data['stage']
        details = profile_data['details']
        notes = profile_data['notes']
        stage_id = profile_data['stage_id']
        date = profile_data['create_date']
        if date is '':
            date = datetime.datetime.now().strftime("%d/%m/%Y")
        date = datetime.datetime.strptime(date, "%d/%m/%Y")
        talent_objs = Talent.objects.filter(id=talent)
        if not talent_objs:
            return util.returnErrorShorcut(400, 'Talent with id {} not found'.format(talent))
        talent_obj = talent_objs[0]
        stageid = TalentStage.objects.filter(id=stage_id)
        if not stageid:
            return util.returnErrorShorcut(400, 'Stage id {} is not exist in database'.format(stage_id))
        created = TalentStage.objects.filter(talent=talent_obj, stage=stage, details=details,
                                             notes=notes,date_created=date).exists()
        if created:
            return util.returnErrorShorcut(400,
                                           'Talent stage and info is exist in database,Please update the stage')
        else:
            Talent.objects.filter(id=talent).update(activation_date=timezone.now())
            updated = TalentStage.objects.filter(id=str(stage_id)).update(stage=stage, details=details,
                                                                          notes=notes, date_created=date)
            if updated:
                queryset = super(TalentStageEditAPI, self).get_queryset()
                queryset = queryset.filter(talent_id=talent)
                serializer_data = TalentSerializer(talent_obj)
                context['result'] = serializer_data.data
                context['message'] = 'Talent Stage Updated Successfully'
                context['success'] = True
                return util.returnSuccessShorcut(context)
        return util.returnSuccessShorcut(context)


# Delete Talent's project Stage
class TalentStageDeleteAPI(generics.ListCreateAPIView):
    queryset = TalentStage.objects.all()
    serializer_class = TalentProjectStageSerializer
    http_method_names = ['get', 'post','delete']

    def delete(self, request, *args, **kwargs):
        context = dict()
        recruiter = request.META.get('HTTP_RECRUITER' '')

        token = request.META.get('HTTP_TOKEN' '')
        is_valid = user_validation(data={'recruiter': recruiter,
                                         'token': token})
        if not is_valid:
            return util.returnErrorShorcut(403, 'Either Recruiter Email or Token id is not valid')
        user = User.objects.filter(username=recruiter)
        id = request.GET['stage_id']
        stage_id = TalentStage.objects.filter(id=id)
        if not stage_id:
            return util.returnErrorShorcut(400, 'Stage id {} not found'.format(id))
        talent_id = request.GET['talent_id']
        talent_objs = Talent.objects.filter(id=talent_id)
        if not talent_objs:
            return util.returnErrorShorcut(400, 'Talent with id {} not found'.format(talent_id))
        talent_obj = talent_objs[0]
        Talent.objects.filter(id=talent_id).update(activation_date=timezone.now())
        TalentStage.objects.filter(id=id,talent=talent_id).delete()
        queryset = super(TalentStageDeleteAPI, self).get_queryset()
        queryset = queryset.filter(talent_id=talent_id)
        serializer_data = TalentSerializer(talent_obj)
        context['result'] = serializer_data.data
        context['message'] = 'Talent Stage Deleted Successfully'
        context['success'] = True
        return util.returnSuccessShorcut(context)


# View All Talent's stages
class TalentAllStageDetailsAPI(View):
    def get(self, request):
        talent_id = request.GET['talent_id']
        talent_obj = Talent.objects.filter(id=talent_id)
        if not talent_obj:
            return util.returnErrorShorcut(400, 'Talent with id {} not found'.format(talent_id))
        queryset = TalentStage.objects.filter(talent=talent_obj)
        serializer_data = TalentStageSerializer(queryset, many=True).data
        talent_stage_all = dict()
        talent_stage_all['result'] = serializer_data
        return util.returnSuccessShorcut(talent_stage_all)


class TalentUpdateRank(View):
    def get(self, request):
        context = dict()
        talent = request.GET['talent_id']
        talent_objs = Talent.objects.filter(id=talent)
        if not talent_objs:
            return util.returnErrorShorcut(400, 'Talent with id {} not found'.format(talent))

        talent = Talent.objects.filter(id=talent)
        if talent:
            talent = talent[0]
            Talent.objects.filter(id=talent_objs).update(activation_date=timezone.now())
            talent.rating = request.GET['rating']
            talent.save()
            context['message'] = 'success'
        return util.returnSuccessShorcut(context)


class TalentAdd(generics.ListCreateAPIView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TalentAdd, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        context = dict()
        recruiter = request.META.get('HTTP_RECRUITER' '')

        token = request.META.get('HTTP_TOKEN' '')
        is_valid = user_validation(data={'recruiter': recruiter,
                                         'token': token})
        if not is_valid:
            return util.returnErrorShorcut(403, 'Either Recruiter Email or Token id is not valid')
        user = User.objects.filter(username=recruiter)
        if user:
            user = user[0]
        profile_data = json.loads(request.body.decode("utf-8"))
        if "id" not in profile_data:
            # phone and email
            # phone = profile_data.get('phone', '')
            email = profile_data.get('email', '')
            # linkedin_url = profile_data.get('linkedinProfileUrl', '')
            if email != '':
                email_talent = TalentEmail.objects.filter(email=email, talent__talent_active__is_active=True)
                if email_talent:
                    return util.returnErrorShorcut(400, 'Talent with this email already exists in the system')
            # profile_data["currentOrganization"].extend(profile_data["pastOrganization"])
            # del profile_data["pastOrganization"]
            add_edit_talent(profile_data, user)
            context['message'] = 'Talent Added Successfully'
            context['success'] = True
            return util.returnSuccessShorcut(context)
        else:
            result = add_edit_talent(profile_data, user)
            if result is False:
                return util.returnErrorShorcut(400, 'Talent with this email already exists in the system')
            # add updated serializer data to context
            else:
                talent_id = profile_data.get('id', '')
                if talent_id:
                    talent = Talent.objects.filter(id=talent_id)
                    if talent:
                        talent = talent[0]
                        Talent.objects.filter(id=talent_id).update(activation_date=timezone.now())
                        Talent.objects.filter(id=talent_id).update(request_by=profile_data.get('request_by', ''))
                        serializer_data = TalentSerializer(talent)
                        context['talent_updated_data'] = serializer_data.data
                context['message'] = 'Talent Updated Successfully'
                context['success'] = True
                return util.returnSuccessShorcut(context)


def add_edit_talent(profile_data, user):
    if "id" in profile_data:
        talent_obj = Talent.objects.filter(id=profile_data.get('id', ''))
        if talent_obj:
            talent_obj.update(talent_name=profile_data.get('firstName', '') + ' ' + profile_data.get('lastName', ''),
                              recruiter=user, status='New',
                              industry_focus=profile_data.get('industryFocus','')['name'],
                              industry_focus_percentage=profile_data.get('industryFocus', '')['percentage'],
                              linkedin_url=profile_data.get('linkedinProfileUrl', ''),
                              image=profile_data.get('profile_image', '')
                              )
            TalentLocation.objects.update(talent=talent_obj[0], city=profile_data.get('city', ''),
                                          state=profile_data.get('state', ''), country=profile_data.get('country', ''))
            talent_obj = talent_obj[0]
            email = profile_data.get('email', '')
            if email != '':
                email_talent = TalentEmail.objects.filter(email=email, talent__talent_active__is_active=True)
                if email_talent:
                    return False
                else:
                    TalentEmail.objects.filter(talent=talent_obj).update(email=profile_data.get('email', ''))
            TalentContact.objects.filter(talent=talent_obj).update(contact=profile_data.get('phone', ''))
    else:
        talent_obj = Talent.objects.create(
            talent_name=profile_data.get('firstName', '') + ' ' + profile_data.get('lastName', ''),
            recruiter=user, status='New', industry_focus=profile_data.get('industryFocus','')['name'],
            industry_focus_percentage=profile_data.get('industryFocus','')['percentage'],
            linkedin_url=profile_data.get('linkedinProfileUrl', ''), image=profile_data.get('profile_image', ''),
            request_by=profile_data.get('request_by', ''),
            create_date=datetime.datetime.now())
        TalentLocation.objects.create(talent=talent_obj,city=profile_data.get('city', ''),
                                      state=profile_data.get('state', ''), country=profile_data.get('country', ''))
        TalentRecruiter.objects.get_or_create(talent=talent_obj, recruiter=user, is_active=True)

        # add email and phone for talent
        TalentEmail.objects.get_or_create(talent=talent_obj, email=profile_data.get('email', ''))
        TalentContact.objects.get_or_create(talent=talent_obj, contact=profile_data.get('phone', ''))

        # add top concepts for talent
        if 'topConcepts' in profile_data:
            for skill in profile_data.get('topConcepts', ''):
                if bool(skill):
                    try:
                        match = float(skill.get('percentage', skill.get('match', '')))
                    except:
                        match = 0
                    if match and match < 1:
                        match *= 100
                        match = round(match, 2)
                    if match and match > 100:
                        match = 100
                    concept, created = Concept.objects.get_or_create(concept=skill.get('name'))
                    TalentConcept.objects.get_or_create(talent=talent_obj, concept=concept, match=match)

    if "education" in profile_data:
        for education in profile_data.get('education', ''):
            # save user education information
            if bool(education):
                talent_education = education.get('name', '')
                if talent_education != "":
                    org, created = Education.objects.get_or_create(name=talent_education)
                    start_date, end_date = education_convert_to_start_end(education)
                    if "id" in education:
                        # update information, check if id is valid or not
                        TalentEducation.objects.filter(id=education.get('id', '')).update(talent=talent_obj,
                                                                                          education=org,
                                                                                          start_date=start_date,
                                                                                          end_date=end_date
                                                                                          )
                    else:
                        if start_date and end_date:
                            TalentEducation.objects.get_or_create(talent=talent_obj, education=org, start_date=start_date,
                                                                  end_date=end_date)
                        else:
                            TalentEducation.objects.get_or_create(talent=talent_obj,education=org)
    if 'currentOrganization' in profile_data:
        for organization in profile_data.get('currentOrganization', ''):
            if bool(organization):
                company_name = organization.get('name')
                if company_name != "":
                    company, created = Company.objects.get_or_create(company_name=organization.get('name', ''))
                    start_date, end_date = convert_to_start_end(organization)
                    if "id" in organization:
                        talent_obj.designation = organization.get('JobTitle', '')
                        talent_obj.save()
                        # update information, check if id is valid or not
                        TalentCompany.objects.filter(id=organization.get('id', '')).update(
                            talent=talent_obj,
                            company=company, designation=organization.get('JobTitle', ''), is_current=True,
                            start_date=start_date)
                    else:
                        talent_obj.designation = organization.get('JobTitle', '')
                        talent_obj.save()
                        if organization.get('is_current', '') is True:
                            if start_date:
                                talent_company, created = TalentCompany.objects.get_or_create(
                                    talent=talent_obj, company=company, designation=organization.get('JobTitle', ''),
                                    start_date=start_date, is_current=True)
                                if end_date:
                                    talent_company.end_date = end_date
                                    talent_company.is_current = True
                                    talent_company.save()
                            else:
                                TalentCompany.objects.get_or_create(
                                    talent=talent_obj, company=company, designation=organization.get('JobTitle', ''),
                                    is_current=organization.get('is_current', ''))
                        else:
                            if start_date:
                                talent_company, created = TalentCompany.objects.get_or_create(
                                    talent=talent_obj, company=company, designation=organization.get('JobTitle', ''),
                                    start_date=start_date,is_current=organization.get('is_current', ''))
                                if end_date:
                                    talent_company.end_date = end_date
                                    talent_company.is_current = True
                                    talent_company.save()
                            else:
                                TalentCompany.objects.get_or_create(
                                    talent=talent_obj, company=company, designation=organization.get('JobTitle', ''),
                                    is_current=True,)
                else:
                    if "id" in organization:
                        TalentCompany.objects.filter(id=organization.get('id', '')).update(
                            talent=talent_obj,
                            company=company_name, designation=organization.get('JobTitle', ''), is_current=True)

    if 'pastOrganization' in profile_data:
        for organization in profile_data.get('pastOrganization', ''):
            if bool(organization):
                company_name = organization.get('name')
                if company_name != "":
                    company, created = Company.objects.get_or_create(company_name=organization.get('name', ''))
                    start_date, end_date = convert_to_start_end(organization)
                    if "id" in organization:
                        talent_obj.designation = organization.get('JobTitle', '')
                        talent_obj.save()
                        # update information, check if id is valid or not
                        TalentCompany.objects.filter(id=organization.get('id', '')).update(
                            talent=talent_obj,
                            company=company, designation=organization.get('JobTitle', ''), is_current=False,
                            start_date=start_date, end_date=end_date)
                    else:
                        talent_obj.designation = organization.get('JobTitle', '')
                        talent_obj.save()
                        if start_date:
                            talent_company, created = TalentCompany.objects.get_or_create(
                                talent=talent_obj, company=company, designation=organization.get('JobTitle', ''),
                                start_date=start_date, is_current=False)
                            if end_date:
                                talent_company.end_date = end_date
                                talent_company.is_current = False
                                talent_company.save()
                        else:
                            TalentCompany.objects.get_or_create(
                                talent=talent_obj, company=company, designation=organization.get('JobTitle', ''),
                                is_current=False)

    if "JobTitle" in profile_data:
        talent_obj.designation = profile_data.get('JobTitle', '')
        talent_obj.save()


def convert_to_start_end(organization):
    end_date = None
    start_date = None
    day = 1
    month = 1
    start_year = organization.get('from')
    end_year = organization.get('to')
    if start_year != "":
        start_date = date(int(start_year), month, day)
        if end_year != "":
            if end_year.strip(" ") == "Present":
                return start_date, end_date
            else:
                end_date = date(int(end_year), month, day)
        return start_date, end_date
    return start_date, end_date


def education_convert_to_start_end(education):
    start_date = None
    end_date = None
    day = 1
    month = 1
    try:
        if education.get('from') != "":
            start_date = date(int(education.get('from')), month, day)
            end_date = date(int(education.get('to')), month, day)
    except:
        pass
    return start_date, end_date


class DeleteTalent(generics.ListCreateAPIView):
    queryset = Talent.objects.all()
    serializer_class = TalentSerializer
    http_method_names = ['get']

    def get_queryset(self):
        queryset = super(DeleteTalent, self).get_queryset()
        recruiter = self.request.query_params.get('recruiter')
        talent_id_list = self.request.query_params.get('talent').split(',')  # ('talent[]')[0].split(',')

        for talent_id in talent_id_list:
            talent_objs = Talent.objects.filter(id=talent_id)
            if not talent_objs:
                return util.returnErrorShorcut(400, 'Talent with id {} dosen\'t exist in database.'.format(talent_id))
            talent_id = talent_objs[0]
            to_delete = TalentRecruiter.objects.filter(talent=talent_id, recruiter__username=recruiter)
            if to_delete:
                to_delete = to_delete[0]
                to_delete.is_active = False
                to_delete.save()

        return queryset.filter(Q(talent_active__is_active=True) & Q(recruiter__username=recruiter) &
                               Q(talent_active__recruiter__username=recruiter) &
                               Q(status__in=['New', 'Active'])).order_by('-create_date')


def talent_validation(user_data):
    values = Talent.objects.filter(talent_name=user_data['talent'], id=user_data['id'])
    if not values:
        return False
    else:
        return True


class LinkedinAddUrl(generics.ListCreateAPIView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LinkedinAddUrl, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        linkedin_url = request.data['url']
        if linkedin_url != '':
            linkedin_talent = Talent.objects.filter(linkedin_url=linkedin_url, talent_active__is_active=True)
            if linkedin_talent:
                return util.returnErrorShorcut(400, 'Linkedin URL is already exists in the system')
        talent_id = request.data['id']
        talent = Talent.objects.filter(id=talent_id)
        Talent.objects.filter(id=talent).update(activation_date=timezone.now())
        if not talent:
            return util.returnErrorShorcut(400, 'Talent with id {} dosen\'t exist in database.'.format(talent_id))
        talent = talent[0]
        # {'lastName': 'Lyden', 'currentOrganization': [{'name': 'BrightStaffer', 'to': 'Present', 'from': ''}],
        #  'city': 'Washington D.C. Metro Area', 'profile_image': 'https://me',
        # 'firstName': 'Matt', 'talent_designation': 'Co-founder, CEO at BrightStaffer'}
        context = dict()
        googleCSE = GoogleCustomSearch()
        content = googleCSE.google_custom(linkedin_url)
        if content=={}:
            context['success'] = False
            return util.returnErrorShorcut(400, "Sorry but the system was unable to locate this linkedin record")
        if content is None:
            context['success'] = False
            return util.returnErrorShorcut(400, "Sorry but the system was unable to locate this linkedin record")
        else:
            talent.talent_name = content['firstName'] + " " + content['lastName']
            talent.designation = content['talent_designation']
            talent.image = content['profile_image']
            talent.linkedin_url = linkedin_url
            talent.save()
            talent_loc, created = TalentLocation.objects.get_or_create(talent=talent)
            talent_loc.city = content['city']
            talent_loc.save()
        context['success'] = True
        return util.returnSuccessShorcut(context)


class TalentSearch(generics.ListCreateAPIView):
    queryset = Talent.objects.all()
    serializer_class = TalentSerializer
    pagination_class = LargeResultsSetPagination

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TalentSearch, self).dispatch(request, *args, **kwargs)

    @required_headers(params=['HTTP_TOKEN', 'HTTP_RECRUITER'])
    def get(self, request, *args, **kwargs):
        recruiter = request.META.get('HTTP_RECRUITER' '')
        token = request.META.get('HTTP_TOKEN', '')

        is_valid = user_validation(data={'recruiter': recruiter,
                                         'token': token})
        if not is_valid:
            return util.returnErrorShorcut(403, 'Either Recruiter Email or Token id is not valid')
        return super(TalentSearch, self).get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(TalentSearch, self).get_queryset()
        term = self.request.GET.get('term', '')
        term = term.strip('"')
        recruiter = self.request.META.get('HTTP_RECRUITER' '')

        # get filter options
        rating = self.request.GET.get('rating', '')
        talent_company = self.request.GET.get('talent_company', '')
        project_match = self.request.GET.get('project_match', '')
        concepts = self.request.GET.get('concepts', '')
        projects = self.request.GET.get('projects', '')
        stages = self.request.GET.get('stages', '')
        last_contacted = self.request.GET.get('last_contacted', '')
        date_added = self.request.GET.get('date_added', '')
        ordering = self.request.GET.get('ordering', '')
        is_active = self.request.GET.get('is_active', '')
        recruiter_param = self.request.GET.get('recruiter', '')

        queryset = queryset.filter(Q(recruiter__username__iexact=recruiter) & Q(talent_active__is_active=True) &
                                   Q(talent_active__recruiter__username=recruiter))
        if term:
            queryset = queryset.filter(
                Q(talent_active__is_active=True) & Q(status__in=['New', 'Active']) &
                Q(talent_name__icontains=term) | Q(designation__icontains=term) |
                Q(current_location__city__icontains=term) | Q(current_location__state__icontains=term) |
                Q(current_location__country__icontains=term) |
                Q(industry_focus__icontains=term) | Q(talent_company__company__company_name__icontains=term) |
                Q(talent_company__designation__icontains=term) |
                Q(talent_project__project__project_name__icontains=term) |
                Q(talent_concepts__concept__concept__icontains=term) | Q(talent_concepts__match__icontains=term) |
                Q(talent_education__education__name__icontains=term) | Q(talent_education__course__icontains=term) |
                Q(talent_email__email__icontains=term) |
                Q(talent_contact__contact__icontains=term) | Q(talent_stages__notes__icontains=term) |
                Q(talent_stages__details__icontains=term))
        if rating:
            queryset = queryset.filter(rating=rating)
        if talent_company:
            queryset = queryset.filter(talent_company__company__company_name__icontains=talent_company)
        if project_match:
            queryset = queryset.filter(talent_project__project_match__gte=int(project_match))
        if concepts:
            concepts = concepts.split(',')
            queryset = queryset.filter(talent_concepts__concept__concept__iregex=r'(' + '|'.join(concepts) + ')')
        if projects:
            # projects = projects.split(',')
            queryset = queryset.filter(talent_project__project__project_name=projects)
        if stages:
            # stages = stages.split(',')
            if projects:
                queryset = queryset.filter(
                    Q(talent_stages__stage=stages) & Q(talent_stages__project__project_name=projects))
            else:
                queryset = queryset.filter(talent_stages__stage=stages)
        if recruiter_param:
            queryset = queryset.filter(recruiter__username=recruiter_param)
        if date_added:
            date_added = datetime.date(int(date_added.split('/')[2]), int(date_added.split('/')[1]),
                                       int(date_added.split('/')[0]))
            queryset = queryset.filter(create_date__range=(datetime.datetime.combine(date_added, datetime.time.min),
                                                           datetime.datetime.combine(date_added, datetime.time.max)))
        if projects:
            queryset = queryset.order_by('-talent_project__project_match')
            return queryset
        if ordering:
            if ordering == "asc":
                queryset = queryset.order_by('create_date')
            if ordering == "desc":
                queryset = queryset.order_by('-create_date')
        if is_active and is_active == "true":
                queryset = queryset.filter(status='Active').order_by('-activation_date')
        if is_active and is_active == "false":
            queryset = queryset.filter(status='InActive')
        else:
            queryset = queryset.filter(status__in=['New', 'Active'])
        if not ordering:
            queryset = queryset.order_by('-create_date')
        return queryset.distinct()



class DeleteOrg(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteOrg, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("405 ERROR:-Method is not allowed")

    def post(self, request):
        param_dict = {}
        profile_data = json.loads(request.body.decode("utf-8"))
        company = TalentCompany.objects.filter(id=profile_data['id'])
        if not company:
            return util.returnErrorShorcut(400, 'Company id {} dosen\'t exist in database.'.format(
                profile_data['id']))
        talent_objs = Talent.objects.filter(id=profile_data['talent_id'])
        if not talent_objs:
            return util.returnErrorShorcut(400, 'Talent with id {} dosen\'t exist in database.'.format(profile_data['talent_id']))
        talent_id = talent_objs[0]
        TalentCompany.objects.filter(talent=talent_id, id=profile_data['id']).delete()
        param_dict['success'] = True
        return util.returnSuccessShorcut(param_dict)


class DeleteEdu(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteEdu, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("405 ERROR:-Method is not allowed")

    def post(self, request):
        param_dict = {}
        profile_data = json.loads(request.body.decode("utf-8"))
        education = TalentEducation.objects.filter(id=profile_data['id'])
        if not education:
            return util.returnErrorShorcut(400, 'Education id {} dosen\'t exist in database.'.format(
                profile_data['id']))
        talent_objs = Talent.objects.filter(id=profile_data['talent_id'])
        if not talent_objs:
            return util.returnErrorShorcut(400, 'Talent with id {} dosen\'t exist in database.'.format(
                profile_data['talent_id']))
        talent_id = talent_objs[0]
        TalentEducation.objects.filter(talent=talent_id, id=profile_data['id']).delete()
        param_dict['success'] = True
        return util.returnSuccessShorcut(param_dict)


class DeleteConcept(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteConcept, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("405 ERROR:-Method is not allowed")

    def post(self, request):
        param_dict = {}
        profile_data = json.loads(request.body.decode("utf-8"))
        concept = TalentConcept.objects.filter(id=profile_data['id'])
        if not concept:
            return util.returnErrorShorcut(400, 'Concept id {} dosen\'t exist in database.'.format(
                profile_data['id']))
        talent_objs = Talent.objects.filter(id=profile_data['talent_id'])
        if not talent_objs:
            return util.returnErrorShorcut(400, 'Talent with id {} dosen\'t exist in database.'.format(
                profile_data['talent_id']))
        talent_id = talent_objs[0]
        TalentConcept.objects.filter(talent=talent_id, id=profile_data['id']).delete()
        param_dict['success'] = True
        return util.returnSuccessShorcut(param_dict)