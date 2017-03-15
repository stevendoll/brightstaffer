from brightStafferapp.models import Talent, Token, Company, User, Projects, TalentProject, TalentEmail, TalentContact, \
    TalentStage, TalentRecruiter
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
from elasticsearch import Elasticsearch


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
        queryset = queryset.filter(talent_active__is_active=True)
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


#Show Talent Profile API
class TalentDetail(generics.RetrieveAPIView):
    queryset = Talent.objects.all()
    model = Talent
    serializer_class = TalentSerializer

    def get_queryset(self):
        queryset = super(TalentDetail, self).get_queryset()
        return queryset

#Show Talent Email and Contact API
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


#Show Talent Contact API
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
        talent_id_list = request.POST.getlist('talent_id[]')[0].split(',')
        for talent_id in talent_id_list:
            talent_objs = Talent.objects.filter(id=talent_id)
            if not talent_objs:
                return util.returnErrorShorcut(403, 'Talent with id {} doesn\'t exist in database.'.format(talent_id))
            talent_obj = talent_objs[0]
            tp_obj, created = TalentProject.objects.get_or_create(talent=talent_obj, project=project)
            if created:
                TalentProject.objects.filter(talent=talent_obj, project=project).update(project_match="50", rank="3")
                #context['message'] = 'success'
            #else:
            #    context['error'] = 'Talent Project object already exists.'
                #return util.returnErrorShorcut(400, context)
        return util.returnSuccessShorcut(context)


# View Talent's Current stage for a sinlge project and Add Talent's stage for a single project
class TalentStageAddAPI(generics.ListCreateAPIView):
    queryset = TalentStage.objects.all()
    serializer_class = TalentProjectStageSerializer
    http_method_names = ['get','post']

    def get_queryset(self):
        queryset = super(TalentStageAddAPI, self).get_queryset()
        talent_id = self.request.query_params.get('talent_id')
        project_id = self.request.query_params.get('project_id')
        stage_id = self.request.query_params.get('stage_id')
        queryset = queryset.filter(id=stage_id,talent_id=talent_id,project_id=project_id)
        return queryset

    def post(self, request, *args, **kwargs):
        context = {}
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
            context['talent_id']=tp_obj.talent.talent_name
            context['stage_id']=tp_obj.id
            context['project']=tp_obj.project.project_name
            context['stage']=tp_obj.stage
            context['details'] = tp_obj.details
            context['notes'] = tp_obj.notes
            return util.returnSuccessShorcut(context)
        else:
            return util.returnErrorShorcut(403, 'Talent stage and info is exist in database,Please create different stage' )


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
        stage_id=request.POST['id']
        projects = Projects.objects.filter(id=project)
        if not projects:
            return util.returnErrorShorcut(403, 'Project with id {} doesn\'t exist in database.'.format(project))
        project = projects[0]
        talent_objs = Talent.objects.filter(id=talent)
        if not talent_objs:
            return util.returnErrorShorcut(404, 'Talent with id {} not found'.format(talent))
        talent_obj = talent_objs[0]
        created = TalentStage.objects.filter(talent=talent_obj, project=project, stage=stage, details=details,
                                                    notes=notes).exists()
        if created:
            return util.returnErrorShorcut(403,
                                           'Talent stage and info is exist in database,Please update the stage')
        else:
            updated=TalentStage.objects.filter(id=str(stage_id)).update(stage=stage,details=details,notes=notes)
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
            return util.returnErrorShorcut(403,'Stage id is not exist in the system')
        is_deleted = TalentStage.objects.filter(id=id).delete()[0]
        return util.returnSuccessShorcut(context)


# View All Talent's project(Single) stages
class TalentAllStageDetailsAPI(generics.ListCreateAPIView):
    queryset = TalentStage.objects.all()
    serializer_class = TalentProjectStageSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        queryset = super(TalentAllStageDetailsAPI, self).get_queryset()
        talent_id = self.request.query_params.get('talent_id')
        project_id = self.request.query_params.get('project_id')
        queryset = queryset.filter(talent_id=talent_id, project_id=project_id)
        return queryset

class TalentUpdateRank(View):
    def get(self,request):
        context={}
        talent = request.GET['talent_id']
        talent_objs = Talent.objects.filter(id=talent)
        if not talent_objs:
            return util.returnErrorShorcut(404, 'Talent with id {} not found'.format(talent))

        updated = Talent.objects.filter(id=talent).update(rating=request.GET['rating'])
        if updated:
            context['message'] = 'success'
        return util.returnSuccessShorcut(context)


class DeleteTalent(generics.ListCreateAPIView):
    queryset = TalentRecruiter.objects.all()
    serializer_class = TalentProjectStageSerializer
    http_method_names = ['get', 'post', 'delete']

    def delete(self, request):
        context = {}
        recruiter = request.GET['recruiter']
        is_active = request.GET['is_active']
        talent_id_list = request.query_params['talent'].split(',') #('talent[]')[0].split(',')

        for talent_id in talent_id_list:
            talent_objs = Talent.objects.filter(id=talent_id)
            if not talent_objs:
                return util.returnErrorShorcut(403, 'Talent with id {} dosen\'t exist in database.'.format(talent_id))
            updated = TalentRecruiter.objects.filter(talent=talent_objs, recruiter__username=recruiter)\
                .update(is_active=is_active)
            if updated:
                context['message'] = 'success'
        return util.returnSuccessShorcut(context)


def talent_validation(user_data):
    values = Talent.objects.filter(talent_name=user_data['talent'], id=user_data['id'])
    if not values:
        return False
    else:
        return True


class TalentSearch(View):

    def get(self, request):
        es = Elasticsearch()
        term = request.GET['term']
        query = {"query": {
            "bool": {
                "should": [
                    {
                        "nested": {
                            "path": "talent_company",
                            "query": {
                                "multi_match": {
                                    "query": term,
                                    "fields": [
                                        "talent_company.company",
                                        "talent_company.talent",
                                        "talent_company.designation"
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "nested": {
                            "path": "talent_project",
                            "query": {
                                "multi_match": {
                                    "query": term,
                                    "fields": [
                                        "talent_project.project",
                                        "talent_project.talent",
                                        "talent_project.project_match",
                                        "talent_project.project_stage"
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "nested": {
                            "path": "talent_concepts",
                            "query": {
                                "multi_match": {
                                    "query": term,
                                    "fields": [
                                        "talent_concepts.concept",
                                        "talent_concepts.match"
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "nested": {
                            "path": "talent_education",
                            "query": {
                                "multi_match": {
                                    "query": term,
                                    "fields": [
                                        "talent_education.education",
                                        "talent_education.course"
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "nested": {
                            "path": "talent_stages",
                            "query": {
                                "multi_match": {
                                    "query": term,
                                    "fields": [
                                        "talent_stages.notes",
                                        "talent_stages.details",
                                        "talent_stages.project"
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "nested": {
                            "path": "talent_email",
                            "query": {
                                "match": {
                                    "talent_email.email": term
                                }
                            }
                        }
                    },
                    {
                        "nested": {
                            "path": "talent_contact",
                            "query": {
                                "match": {
                                    "talent_contact.contact": term
                                }
                            }
                        }
                    },
                    {
                        "multi_match": {
                            "query": term,
                            "fields": [
                                "talent_name",
                                "designation",
                                "company",
                                "current_location",
                                "industry_focus"
                            ]
                        }
                    }
                ]
            }
        }
        }
        print(query['query']['bool']['should'])
        body = json.dumps(query)
        res = es.search(index="haystack", doc_type="modelresult",
                        body=body
                        )
        return HttpResponse(json.dumps(res['hits']))


class TalentSearchFilter(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TalentSearchFilter, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        es = Elasticsearch()
        rating = request.GET.get('rating', '')
        talent_company = request.GET.get('talent_company', '')
        project_match = request.GET.get('project_match', '')
        recruiter = request.GET.get('recruiter', '')
        concepts = request.GET.get('concepts', '')
        projects = request.GET.get('projects', '')
        stages = request.GET.get('stages', '')
        last_contacted = request.GET.get('last_contacted', '')
        date_added = request.GET.get('date_added', '')

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
                                "gte": project_match
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
                "range": {
                    "rating": {
                        "gte": rating
                    }
                }
            }
            query['query']['bool']['must'].append(rating_query)
        print(query)
        body = json.dumps(query)
        res = es.search(index="haystack", doc_type="modelresult",
                        body=body
                        )
        return HttpResponse(json.dumps(res['hits']))