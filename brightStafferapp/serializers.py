from rest_framework import serializers
from brightStafferapp.models import Projects, Concept, Talent, Education, Company, TalentProject, TalentConcept, \
    TalentCompany
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name="user-detail")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password')


class ConceptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Concept
        fields = ('concept',)


class ProjectSerializer(serializers.ModelSerializer):
    recruiter = serializers.CharField()

    class Meta:
        model = Projects
        fields = ('id', 'get_date', 'location', 'recruiter', 'project_name', 'company_name')
        depth = 1


class TopProjectSerializer(serializers.ModelSerializer):
    concepts = serializers.StringRelatedField(many=True, )

    class Meta:
        model = Projects
        fields = ('id', 'get_date', 'location', 'concepts', 'project_name', 'company_name')


class EducationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Education
        fields = '__all__'


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'


class TalentProjectSerializer(serializers.ModelSerializer):
    project = serializers.CharField()
    talent = serializers.CharField()
    company_name = serializers.CharField()

    class Meta:
        model = TalentProject
        fields = '__all__'


class TalentConceptSerializer(serializers.ModelSerializer):
    talent = serializers.CharField()
    concept = serializers.CharField()

    class Meta:
        model = TalentConcept
        fields = '__all__'


class TalentCompanySerializer(serializers.ModelSerializer):
    talent = serializers.CharField()
    company = serializers.CharField()
    years_of_experience = serializers.CharField()

    class Meta:
        model = TalentCompany
        fields = '__all__'


class TalentSerializer(serializers.ModelSerializer):
    talent_name = serializers.CharField()
    education = EducationSerializer(many=True, )
    recruiter = serializers.CharField()
    talent_company = TalentCompanySerializer(many=True)
    talent_project = TalentProjectSerializer(many=True)
    talent_concepts = TalentConceptSerializer(many=True)

    class Meta:
        model = Talent
        fields = ('id', 'talent_name', 'email_id', 'recruiter', 'get_date', 'current_location', 'talent_company',
                  'education', 'talent_project', 'talent_concepts',)
