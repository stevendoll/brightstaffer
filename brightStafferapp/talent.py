from brightStafferapp.models import Talent, Token, Company
from brightStafferapp.serializers import TalentSerializer
from brightStafferapp import util
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.response import Response
from django.views.generic import View
from rest_framework import generics
import json
from brightStafferapp.views import user_validation


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
        response.data['talent_list'] = response.data['results']
        response.data['message'] = 'success'
        del (response.data['results'])
        return response


class InsertTalent(generics.ListCreateAPIView):
    queryset = Talent.objects.all()
    serializer_class = TalentSerializer
    pagination_class = LargeResultsSetPagination
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        param_dict = {"abc":"xyz"}
        user_data = json.loads(request.body.decode("utf-8"))
        print (user_data)

        for item in user_data['company']:
            company_check = Company.objects.filter(company_name=item['company_name'])
            if not company_check:
                company = Company()
                print (company_check)
                company.company_name = item['company_name']
                company.save()
        return util.returnSuccessShorcut(param_dict)

