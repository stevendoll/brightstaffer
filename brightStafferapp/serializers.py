from rest_framework import serializers
from brightStafferapp.models import Projects, Concept
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="user-detail")

    class Meta:
        model = User
        fields = ('url', 'username')


class ConceptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Concept
        fields = ('concept',)


class ProjectSerializer(serializers.ModelSerializer):
    recruiter = serializers.CharField()

    class Meta:
        model = Projects
        fields = ('id', 'get_date', 'location', 'recruiter', 'project_name', 'company_name')


class TopProjectSerializer(serializers.ModelSerializer):
    #recruiter = serializers.CharField()
    concepts = serializers.StringRelatedField(many=True, )
    # concepts = ConceptSerializer(many=True)

    class Meta:
        model = Projects
        fields = ('id', 'get_date', 'location', 'concepts', 'project_name', 'company_name')