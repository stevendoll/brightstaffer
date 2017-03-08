from brightStafferapp.models import Talent, Token, Company, User, Projects,TalentProject
from brightStafferapp.serializers import TalentSerializer, ProjectSerializer
from brightStafferapp import util
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.response import Response
from django.views.generic import View
from rest_framework import generics
import json
from brightStafferapp.views import user_validation
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, HttpResponse

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
        return Talent.objects.filter(recruiter__username=self.request.query_params['recruiter']) \
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


class ContactInfo(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ContactInfo, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("405 ERROR:-Method is not allowed")

    def post(self, request):
        param_dict = {}
        user_data = json.loads(request.body.decode("utf-8"))
        check_auth = talent_validation(user_data)
        if not check_auth:
            return util.returnErrorShorcut(403, 'Either Talent Name or Talent id is not valid')

        else:
            contact_info=Talent.objects.filter(id=user_data['id']).values('email_id','contact_number')
            for contact in contact_info:
                param_dict['email_id'] = contact['email_id']
                param_dict['contact_number'] = contact['contact_number']
            return util.returnSuccessShorcut(param_dict)


class ProjectAddView(View):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    http_method_names = ['post']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ProjectAddView, self).dispatch(request, *args, **kwargs)

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


def talent_validation(user_data):
    values = Talent.objects.filter(talent_name=user_data['talent'], id=user_data['id'])
    if not values:
        return False
    else:
        return True