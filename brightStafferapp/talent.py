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
            return util.returnErrorShorcut(400, 'Talent with id {} not found'.format(talent_id))
        talent_obj = talent_objs[0]
        if contact:
            is_deleted = TalentContact.objects.filter(talent=talent_obj, contact=contact).delete()[0]
            if not is_deleted:
                return util.returnErrorShorcut(400, 'No entry found or already deleted')
            return util.returnSuccessShorcut(context)
        else:
            return util.returnErrorShorcut(400, 'Contact not found')


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
            return util.returnErrorShorcut(400, 'Talent with id {} not found'.format(talent_id))
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
        email = request.GET['email']
        talent_id = request.GET['talent_id']
        talent_objs = Talent.objects.filter(id=talent_id)
        if not talent_objs:
            return util.returnErrorShorcut(400, 'Talent with id {} not found'.format(talent_id))
        talent_obj = talent_objs[0]
        if email:
            is_deleted = TalentEmail.objects.filter(talent=talent_obj, email=email).delete()[0]
            if not is_deleted:
                return util.returnErrorShorcut(400, 'No entry found or already deleted')
            return util.returnSuccessShorcut(context)
        else:
            return util.returnErrorShorcut(400, 'Email not found')

    def validate_email(self, email):
        users = User.objects.filter(Q(email=email) | Q(username=email))
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

            #TalentProject.objects.filter(talent=talent_obj, project=project).update(project_match="50", rank="3")
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
                if ratio >= 100:
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
                if ratio >= 100:
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
        tp_obj, created = TalentStage.objects.get_or_create(talent=talent_obj, project=project, stage=stage,
                                                            details=details, notes=notes, date_created=date)
        if created:
            context['talent_id']=tp_obj.talent.talent_name
            context['stage_id']=tp_obj.id
            context['project']=tp_obj.project.project_name
            context['stage']=tp_obj.stage
            context['details'] = tp_obj.details
            context['notes'] = tp_obj.notes
            context['create_date'] = tp_obj.get_date_created
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
        date = datetime.datetime.strptime(date, "%d/%m/%Y")
        #projects = Projects.objects.filter(id=project)
        #if not projects:
        #    return util.returnErrorShorcut(400, 'Project with id {} doesn\'t exist in database.'.format(project))
        #project = projects[0]
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
            updated = TalentStage.objects.filter(id=str(stage_id)).update(stage=stage, details=details,
                                                                          notes=notes, date_created=date)
            if updated:
                queryset = super(TalentStageEditAPI, self).get_queryset()
                queryset = queryset.filter(talent_id=talent)
                serializer_data = TalentProjectStageSerializer(queryset, many=True).data
                context['result'] = serializer_data
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
        TalentStage.objects.filter(id=id,talent=talent_id).delete()
        queryset = super(TalentStageDeleteAPI, self).get_queryset()
        queryset = queryset.filter(talent_id=talent_id)
        serializer_data = TalentProjectStageSerializer(queryset, many=True).data
        context['result'] = serializer_data
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
            phone = profile_data.get('phone', '')
            email = profile_data.get('email', '')
            linkedin_url = profile_data.get('linkedinProfileUrl', '')
            talent_linkedin = Talent.objects.filter(linkedin_url=linkedin_url)
            if talent_linkedin != '':
                if talent_linkedin:
                    return util.returnErrorShorcut(400, 'Talent with this linkedin url already exists in the system')
            if email != '':
                email_talent = TalentEmail.objects.filter(email=email)
                if email_talent:
                    return util.returnErrorShorcut(400, 'Talent with this email already exists in the system')
            if phone != '':
                phone_client = TalentContact.objects.filter(contact=phone)
                if phone_client:
                    return util.returnErrorShorcut(400, 'Talent with this contact already exists in the system')
            profile_data["currentOrganization"].extend(profile_data["pastOrganization"])
            del profile_data["pastOrganization"]
            add_edit_talent(profile_data, user)
            context['message'] = 'Talent Added Successfully'
            context['success'] = True
            return util.returnSuccessShorcut(context)
        else:
            add_edit_talent(profile_data, user)
            # add updated serializer data to context
            talent_id = profile_data.get('id', '')
            if talent_id:
                talent = Talent.objects.filter(id=talent_id)
                if talent:
                    talent = talent[0]
                    serializer_data = TalentSerializer(talent)
                    context['talent_updated_data'] = serializer_data.data
            context['message'] = 'Talent Updated Successfully'
            context['success'] = True
            return util.returnSuccessShorcut(context)


def add_edit_talent(profile_data, user):
    if "id" in profile_data:
        talent_obj = Talent.objects.filter(id=profile_data.get('id', ''))
        if talent_obj:
            talent_location, created = TalentLocation.objects.get_or_create(talent=talent_obj[0],
                                                                            city=profile_data.get('city', ''),
                                                                            state=profile_data.get('state', ''),
                                                                            country=profile_data.get('country', '')
                                                                            )
            talent_obj.update(talent_name=profile_data.get('firstName', '') + ' ' + profile_data.get('lastName', ''),
                              recruiter=user, status='New',
                              linkedin_url=profile_data.get('linkedinProfileUrl', ''),
                              industry_focus=profile_data.get('industryFocus', ''))
            talent_obj = talent_obj[0]
    else:
        talent_obj = Talent.objects.create(
            talent_name=profile_data.get('firstName', '') + ' ' + profile_data.get('lastName', ''),
            recruiter=user, status='New', industry_focus=profile_data.get('industryFocus', ''),
            linkedin_url=profile_data.get('linkedinProfileUrl', ''), image=profile_data.get('profile_image', ''),
            create_date=datetime.datetime.now())
        talent_location = TalentLocation.objects.create(talent=talent_obj,
                                                        city=profile_data.get('city', ''),
                                                        state=profile_data.get('state', ''),
                                                        country=profile_data.get('country', ''),

                                                        )
        talent_recruiter, created = TalentRecruiter.objects.get_or_create(talent=talent_obj, recruiter=user,
                                                                          is_active=True)
    if talent_obj:
        # add email and phone for talent
        TalentEmail.objects.get_or_create(talent=talent_obj, email=profile_data.get('email', ''))
        TalentContact.objects.get_or_create(talent=talent_obj, contact=profile_data.get('phone', ''))
        # add top concepts for talent
        if 'topConcepts' in profile_data:
            for skill in profile_data.get('topConcepts', ''):
                if bool(skill):
                    match = float(skill.get('percentage', skill.get('score', '')))
                    if match and match < 1:
                        match *= 100
                        match = round(match, 2)
                    if match and match > 100:
                        match = 100
                    concept, created = Concept.objects.get_or_create(concept=skill.get('name'))
                    tpconcept, created = TalentConcept.objects.get_or_create(talent=talent_obj, concept=concept,
                                                                             match=match)

    if "education" in profile_data:
        for education in profile_data.get('education', ''):
            # save user education information
            if bool(education):
                education = education.get('name', '')
                if education != "":
                    org, created = Education.objects.get_or_create(name=education.get('name', ''))
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
                            tporg, created = TalentEducation.objects.get_or_create(talent=talent_obj,
                                                                                   education=org,
                                                                                   start_date=start_date,
                                                                                   end_date=end_date
                                                                                   )
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
                        if start_date:
                            talent_company, created = TalentCompany.objects.get_or_create(
                                talent=talent_obj, company=company, designation=organization.get('JobTitle', ''),
                                start_date=start_date)
                            if end_date:
                                talent_company.end_date = end_date
                                talent_company.is_current = False
                        else:
                            talent_company, created = TalentCompany.objects.get_or_create(
                                talent=talent_obj, company=company, designation=organization.get('JobTitle', ''))

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
    if start_year != "" and end_year != "":
        start_date = date(int(start_year), month, day)

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
            projects = projects.split(',')
            queryset = queryset.filter(talent_project__project__project_name__in=projects)
        if stages:
            stages = stages.split(',')
            queryset = queryset.filter(talent_stages__stage__in=stages)
        if recruiter_param:
            queryset = queryset.filter(recruiter__username=recruiter_param)
        if date_added:
            date_added = datetime.date(int(date_added.split('/')[2]), int(date_added.split('/')[1]),
                                       int(date_added.split('/')[0]))
            queryset = queryset.filter(create_date__range=(datetime.datetime.combine(date_added, datetime.time.min),
                                                           datetime.datetime.combine(date_added, datetime.time.max)))
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


# class TalentSearch(generics.ListCreateAPIView):
#     serializer_class = TalentSerializer
#
#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         return super(TalentSearch, self).dispatch(request, *args, **kwargs)
#
#     @required_headers(params=['HTTP_TOKEN', 'HTTP_RECRUITER'])
#     def get(self, request, *args, **kwargs):
#         es = Elasticsearch(hosts=[settings.HAYSTACK_CONNECTIONS['default']['URL']])
#         term = request.GET.get('term', '')
#         recruiter = request.META.get('HTTP_RECRUITER' '')
#         token = request.META.get('HTTP_TOKEN', '')
#         count = request.GET.get('count', '')
#         page = request.GET.get('page', '')
#         is_valid = user_validation(data={'recruiter': recruiter,
#                                          'token': token})
#         if not is_valid:
#             return util.returnErrorShorcut(403, 'Either Recruiter Email or Token id is not valid')
#         term = term.strip('"')
#         term_query = copy.deepcopy(TERM_QUERY)
#         term_query['from'] = 0 if int(page) == 1 else int(page) - 2 + ((int(page) - 1) * 10)
#         term_query['size'] = count
#         try:
#             if term:
#                 body = json.loads(re.sub(r"\brecruiter_term\b", recruiter,
#                                          re.sub(r"\bsearch_term\b", term, json.dumps(term_query))))
#                 res = es.search(index="haystack", doc_type="modelresult",
#                                 body=body
#                                 )
#                 return HttpResponse(json.dumps(res['hits']))
#             else:
#                 base_query = copy.deepcopy(BASE_QUERY)
#                 base_query['from'] = 0 if int(page) == 1 else int(page) - 2 + ((int(page) - 1) * 10)
#                 base_query['size'] = count
#                 base_query = json.loads(re.sub(r"\brecruiter_term\b", recruiter, json.dumps(base_query)))
#                 res = es.search(index="haystack", doc_type="modelresult",
#                                 body=base_query
#                                 )
#                 return HttpResponse(json.dumps(res['hits']))
#         except:
#             return HttpResponse(json.dumps(EMPTY_QUERY))


class TalentSearchFilter(generics.ListCreateAPIView):
    serializer_class = TalentSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TalentSearchFilter, self).dispatch(request, *args, **kwargs)

    @required_headers(params=['HTTP_TOKEN', 'HTTP_RECRUITER'])
    def get(self, request, *args, **kwargs):
        es = Elasticsearch(hosts=[settings.HAYSTACK_CONNECTIONS['default']['URL']])
        recruiter = request.META.get('HTTP_RECRUITER' '')
        recruiter_param = request.GET.get('recruiter', '')
        token = request.META.get('HTTP_TOKEN', '')
        is_valid = user_validation(data={'recruiter': recruiter,
                                         'token': token})
        if not is_valid:
            return util.returnErrorShorcut(403, 'Either Recruiter Email or Token id is not valid')

        rating = request.GET.get('rating', '')
        talent_company = request.GET.get('talent_company', '')
        project_match = request.GET.get('project_match', '')
        concepts = request.GET.get('concepts', '')
        projects = request.GET.get('projects', '')
        stages = request.GET.get('stages', '')
        last_contacted = request.GET.get('last_contacted', '')
        date_added = request.GET.get('date_added', '')
        term = request.GET.get('term', '')
        ordering = request.GET.get('ordering', '')
        is_active = request.GET.get('is_active', '')
        count = request.GET.get('count', '')
        page = request.GET.get('page', '')

        query = copy.deepcopy(BASE_QUERY)
        if date_added:
            date_added_query = {
                "match": {
                    "create_date": date_added
                }
            }
            query['query']['bool']['filter']['bool']['must'].append(date_added_query)

        if last_contacted:
            last_contacted_query = {
                "nested": {
                    "path": "talent_stages",
                    "query": {
                        "match": {
                            "talent_stages.date_updated": last_contacted
                        }
                    },
                }
            }
            query['query']['bool']['filter']['bool']['must'].append(last_contacted_query)
        if stages:
            for stage in stages.split(','):
                stage_query = {
                    "nested": {
                        "path": "talent_stages",
                        "query": {
                            "multi_match": {
                                "query": stage,
                                "fields": [
                                    "talent_stages.stage"
                                ]
                            }
                        }
                    }
                }
                query['query']['bool']['filter']['bool']['must'].append(stage_query)

        if projects:
            for project in projects.split(','):
                project_query = {
                    "nested": {
                        "path": "talent_project",
                        "query": {
                            "multi_match": {
                                "query": project,
                                "fields": [
                                    "talent_project.project"
                                ]
                            }
                        }
                    }
                }
                query['query']['bool']['filter']['bool']['must'].append(project_query)
        if concepts:
            for concept in concepts.split(','):
                concepts_query = {
                    "nested": {
                        "path": "talent_concepts",
                        "query": {
                            "multi_match": {
                                "query": concept,
                                "fields": [
                                    "talent_concepts.concept"
                                ]
                            }
                        }
                    }
                }
                query['query']['bool']['filter']['bool']['must'].append(concepts_query)
        if recruiter_param:
            recruiter_query = {
                "match": {
                    "recruiter": recruiter_param
                }
            }
            query['query']['bool']['filter']['bool']['must'].append(recruiter_query)
        if project_match:
            project_match_query = {
                "nested": {
                    "query": {
                        "range": {
                            "talent_project.project_match": {
                                "gte": int(project_match),
                            }
                        }
                    },
                    "path": "talent_project"
                }
            }
            query['query']['bool']['filter']['bool']['must'].append(project_match_query)

        if talent_company:
            talent_company_query = {
                "nested": {
                    "path": "talent_company",
                    "query": {
                        "multi_match": {
                            "query": talent_company,
                            "fields": [
                                "talent_company.company",
                                "talent_company.talent",
                                "talent_company.designation"
                            ]
                        }
                    }
                }
            }
            query['query']['bool']['filter']['bool']['must'].append(talent_company_query)

        if rating:
            rating_query = {
                "match": {
                    "rating": rating
                }
            }
            query['query']['bool']['filter']['bool']['must'].append(rating_query)
        if ordering:
            query['sort'] = [
                                {
                                    "create_date": {
                                        "order": ordering
                                    }
                                }
                            ]
        if is_active and is_active == 'true':
            query['sort'] = [
                {
                    "activation_date": {
                        "order": "desc"
                    }
                }
            ]
            is_active_query = {
                "match": {
                    "status": "Active"
                }
            }
            query['query']['bool']['filter']['bool']['must'].append(is_active_query)

        if is_active:
                if is_active == 'false':
                    is_active_query = {
                        "match": {
                            "status": 'InActive'
                        }
                    }
                    query['query']['bool']['filter']['bool']['must'].append(is_active_query)

        if term:
            term_query = copy.deepcopy(TERM_QUERY)
            term_query = json.loads(re.sub(r"\brecruiter_term\b", recruiter,
                                           re.sub(r"\bsearch_term\b", term, json.dumps(term_query))))
            query = json.loads(re.sub(r"\brecruiter_term\b", recruiter,
                                      re.sub(r"\bsearch_term\b", term, json.dumps(query))))

            term_query_should = term_query['query']['bool']['filter']['bool']['should']
            term_query_must = term_query['query']['bool']['filter']['bool']['must']
            term_query_must = json.loads(re.sub(r"\brecruiter_term\b", recruiter,  json.dumps(term_query_must)))
            query['query']['bool']['filter']['bool']['must'].extend(term_query_must)
            query['query']['bool']['filter']['bool']['should'].extend(term_query_should)
        else:
            query = json.loads(re.sub(r"\brecruiter_term\b", recruiter, json.dumps(query)))
        query['from'] = 0 if int(page) == 1 else int(page) - 2 + ((int(page) - 1) * 10)
        query['size'] = count
        res = es.search(index="haystack", doc_type="modelresult", body=query)
        return HttpResponse(json.dumps(res['hits']))


