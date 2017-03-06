from brightStafferapp.models import Talent, Token, Company, User
from brightStafferapp.serializers import TalentSerializer
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
            return super(TalentList, self).get(request, *args, *kwargs)

    def get_queryset(self):
        return Talent.objects.filter(recruiter__username=self.request.query_params['recruiter']) \
            .order_by('-create_date')

    def list(self, request, *args, **kwargs):
        response = super(TalentList, self).list(request, *args, **kwargs)
        user_profile = User.objects.values('first_name', 'last_name').filter(
            username=self.request.query_params['recruiter'])
        for user in user_profile:
            response.data['recruiter_first_name'] = user['first_name']
            response.data['recruiter_last_name'] = user['last_name']
        response.data['talent_list'] = response.data['results']
        response.data['message'] = 'success'
        del (response.data['results'])
        return response

#
# class InsertTalent(generics.ListCreateAPIView):
#     queryset = Talent.objects.all()
#     serializer_class = TalentSerializer
#     pagination_class = LargeResultsSetPagination
#     http_method_names = ['post']
#
#     def post(self, request, *args, **kwargs):
#         param_dict = {"abc":"xyz"}
#         user_data = json.loads(request.body.decode("utf-8"))
#         print (user_data)
#         for item in user_data['company']:
#             company_check = Company.objects.filter(company_name=item['company_name'])
#             if not company_check:
#                 company = Company()
#                 print (company_check)
#                 company.company_name = item['company_name']
#                 company.save()
#         return util.returnSuccessShorcut(param_dict)

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
            print(contact_info)
            for contact in contact_info:
                param_dict['email_id'] = contact['email_id']
                param_dict['contact_number'] = contact['contact_number']
            return util.returnSuccessShorcut(param_dict)



def talent_validation(user_data):
    values = Talent.objects.filter(talent_name=user_data['talent'], id=user_data['id'])
    if not values:
        return False
    else:
        return True