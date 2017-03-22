from brightStafferapp.models import Talent, User, Projects, TalentProject, TalentEmail, TalentContact, \
    TalentStage, TalentRecruiter
from brightStafferapp.serializers import TalentSerializer, TalentContactEmailSerializer, TalentProjectStageSerializer
from brightStafferapp import util
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
import json
import re
from brightStafferapp.util import required_post_params
from brightStafferapp.views import user_validation
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse
from django.db.models import Q
from elasticsearch import Elasticsearch
from datetime import datetime
from .search import TERM_QUERY
from django.conf import settings


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
        queryset = super(TalentList, self).get_queryset()
        count = self.request.query_params['count']
        self.pagination_class.page_size = count
        queryset = queryset.filter(talent_active__is_active=True).order_by('-create_date')[:int(count)]
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
            return util.returnErrorShorcut(403, 'Project with id {} doesn\'t exist in database.'.format(project_id))
        project = projects[0]
        # get list of talent ids from POST request
        talent_id_list = self.request.query_params.get('talent_id[]').split(',')
        for talent_id in talent_id_list:
            talent_objs = Talent.objects.filter(id=talent_id)
            if not talent_objs:
                return util.returnErrorShorcut(403, 'Talent with id {} doesn\'t exist in database.'.format(talent_id))
            talent_obj = talent_objs[0]
            tp_obj, created = TalentProject.objects.get_or_create(talent=talent_obj, project=project)
            TalentProject.objects.filter(talent=talent_obj, project=project).update(project_match="50", rank="3")
            talent_result = queryset.filter(talent_active__is_active=True)
        return talent_result


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
        date = datetime.strptime(date, "%d/%m/%Y")
        projects = Projects.objects.filter(id=project)
        if not projects:
            return util.returnErrorShorcut(403, 'Project with id {} doesn\'t exist in database.'.format(project))
        project = projects[0]
        talent_objs = Talent.objects.filter(id=talent)
        if not talent_objs:
            return util.returnErrorShorcut(404, 'Talent with id {} not found'.format(talent))
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
            return util.returnSuccessShorcut(context)
        else:
            return util.returnErrorShorcut(403, 'Talent stage and info is exist in database, '
                                                'Please create different stage')


# Edit Talent's Stage
class TalentStageEditAPI(generics.ListCreateAPIView):
    queryset = TalentStage.objects.all()
    serializer_class = TalentProjectStageSerializer
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        context = {}
        talent = request.POST['talent_id']
        project = request.POST['project_id']
        stage = request.POST['stage']
        details = request.POST['details']
        notes = request.POST['notes']
        stage_id = request.POST['id']
        date = request.POST['date']
        date = datetime.strptime(date, "%d/%m/%Y")
        projects = Projects.objects.filter(id=project)
        if not projects:
            return util.returnErrorShorcut(403, 'Project with id {} doesn\'t exist in database.'.format(project))
        project = projects[0]
        talent_objs = Talent.objects.filter(id=talent)
        if not talent_objs:
            return util.returnErrorShorcut(404, 'Talent with id {} not found'.format(talent))
        talent_obj = talent_objs[0]
        stageid = TalentStage.objects.filter(id=stage_id)
        if not stageid:
            return util.returnErrorShorcut(404, 'Stage id {} is not exist in database'.format(stage_id))
        created = TalentStage.objects.filter(talent=talent_obj, project=project, stage=stage, details=details,
                                             notes=notes,date_created=date).exists()
        if created:
            return util.returnErrorShorcut(403,
                                           'Talent stage and info is exist in database,Please update the stage')
        else:
            updated = TalentStage.objects.filter(id=str(stage_id)).update(stage=stage, details=details,
                                                                          notes=notes, date_created=date)
            if updated:
                context['message'] = 'success'
        return util.returnSuccessShorcut(context)


# Delete Talent's project Stage
class TalentStageDeleteAPI(generics.ListCreateAPIView):
    queryset = TalentStage.objects.all()
    serializer_class = TalentProjectStageSerializer
    http_method_names = ['get', 'post','delete']

    def delete(self, request, *args, **kwargs):
        context = dict()
        id = request.GET['stage_id']
        talent_id = TalentStage.objects.filter(id=id)
        if not talent_id:
            return util.returnErrorShorcut(403, 'Stage id is not exist in the system')
        TalentStage.objects.filter(id=id).delete()
        return util.returnSuccessShorcut(context)


# View All Talent's stages
class TalentAllStageDetailsAPI(View):

    def get(self, request):

        talent_id = request.GET['talent_id']
        talent_obj = Talent.objects.filter(id=talent_id)
        if not talent_obj:
            return util.returnErrorShorcut(404, 'Talent with id {} not found'.format(talent_id))
        queryset = TalentStage.objects.filter(talent=talent_obj)
        talent_stage = []
        for obj in queryset:
            response = dict()
            response['talent_id'] = obj.talent.talent_name
            response['stage_id'] = obj.id
            response['project'] = obj.project.project_name
            response['stage'] = obj.stage
            response['details'] = obj.details
            response['notes'] = obj.notes
            response['create_date'] = obj.get_date_created
            talent_stage.append(response)
        talent_stage_all = dict()
        talent_stage_all['result'] = talent_stage
        return util.returnSuccessShorcut(talent_stage_all)


class TalentUpdateRank(View):

    def get(self, request):
        context = dict()
        talent = request.GET['talent_id']
        talent_objs = Talent.objects.filter(id=talent)
        if not talent_objs:
            return util.returnErrorShorcut(404, 'Talent with id {} not found'.format(talent))

        updated = Talent.objects.filter(id=talent).update(rating=request.GET['rating'])
        if updated:
            context['message'] = 'success'
        return util.returnSuccessShorcut(context)


class DeleteTalent(generics.ListCreateAPIView):
    queryset = Talent.objects.all()
    serializer_class = TalentSerializer
    http_method_names = ['get']

    def get_queryset(self):
        queryset = super(DeleteTalent, self).get_queryset()
        talent_result = None
        recruiter = self.request.query_params.get('recruiter')
        is_active = self.request.query_params.get('is_active')
        talent_id_list = self.request.query_params.get('talent').split(',')  # ('talent[]')[0].split(',')

        for talent_id in talent_id_list:
            talent_objs = Talent.objects.filter(id=talent_id)
            if not talent_objs:
                return util.returnErrorShorcut(403, 'Talent with id {} dosen\'t exist in database.'.format(talent_id))
            updated = TalentRecruiter.objects.filter(talent=talent_objs, recruiter__username=recruiter)\
                .update(is_active=is_active)
            if updated:
                talent_result = queryset.filter(talent_active__is_active=True)
        return talent_result


def talent_validation(user_data):
    values = Talent.objects.filter(talent_name=user_data['talent'], id=user_data['id'])
    if not values:
        return False
    else:
        return True


class TalentSearch(View):

    def get(self, request):
        es = Elasticsearch(hosts=[settings.HAYSTACK_CONNECTIONS['default']['URL']])
        term = request.GET.get('term', '')
        term = term.strip('"')
        query = TERM_QUERY
        res = {
            "hits": [],
            "max_score": "null",
            "total": 0
        }
        try:
            if term:
                term_query = json.dumps(query)
                term_query = re.sub(r"\bsearch_term\b", term, term_query)
                term_query = json.loads(term_query)
                body = json.dumps(term_query)
                res = es.search(index="haystack", doc_type="modelresult",
                                body=body
                                )
                return HttpResponse(json.dumps(res['hits']))
            else:
                res = es.search(index="haystack", doc_type="modelresult",
                                body=query
                                )
                return HttpResponse(json.dumps(res['hits']))
        except:
            return HttpResponse(json.dumps(res))


class TalentSearchFilter(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TalentSearchFilter, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        es = Elasticsearch(hosts=[settings.HAYSTACK_CONNECTIONS['default']['URL']])
        rating = request.GET.get('rating', '')
        talent_company = request.GET.get('talent_company', '')
        project_match = request.GET.get('project_match', '')
        recruiter = request.GET.get('recruiter', '')
        concepts = request.GET.get('concepts', '')
        projects = request.GET.get('projects', '')
        stages = request.GET.get('stages', '')
        last_contacted = request.GET.get('last_contacted', '')
        date_added = request.GET.get('date_added', '')
        term = request.GET.get('term', '')
        ordering = request.GET.get('ordering', '')
        is_active = request.GET.get('is_active', '')

        query = {
                  "query": {
                    "bool": {
                      "must": [
                      ]
                    }
                  }
                }
        if date_added:
            date_added_query = {
                "match": {
                    "create_date": date_added
                }
            }
            query['query']['bool']['must'].append(date_added_query)

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
            query['query']['bool']['must'].append(last_contacted_query)
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
                query['query']['bool']['must'].append(stage_query)

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
                query['query']['bool']['must'].append(project_query)
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
                query['query']['bool']['must'].append(concepts_query)
        if recruiter:
            recruiter_query = {
                "match": {
                    "recruiter": "chandanvarma2@gmail.com"
                }
            }
            query['query']['bool']['must'].append(recruiter_query)
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
            query['query']['bool']['must'].append(project_match_query)

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
            query['query']['bool']['must'].append(talent_company_query)

        if rating:
            rating_query = {
                "match": {
                    "rating": rating
                }
            }
            query['query']['bool']['must'].append(rating_query)
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
            query['query']['bool']['must'].append(is_active_query)

        if is_active:
                if is_active == 'false':
                    is_active_query = {
                        "match": {
                            "status": 'InActive'
                        }
                    }
                    query['query']['bool']['must'].append(is_active_query)

        if term:
            term_query = TERM_QUERY
            term_query = json.dumps(term_query)
            term_query = re.sub(r"\bsearch_term\b", term, term_query)
            term_query = json.loads(term_query)
            term_query = term_query['query']['bool']['should']
            filtered_query = dict()
            filtered_query['filter'] = dict()
            filtered_query['filter']['bool'] = dict()
            filtered_query['filter']['bool']['should'] = term_query
            filtered_query['filter']['bool']['must'] = query['query']['bool']['must']
            query = {
                      "query": {
                        "bool": {
                          "must": {
                            "match_all": {}
                          }
                        }
                      }
                    }
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
            query['query']['bool'].update(filtered_query)
        body = json.dumps(query)
        res = es.search(index="haystack", doc_type="modelresult", body=body)
        return HttpResponse(json.dumps(res['hits']))
