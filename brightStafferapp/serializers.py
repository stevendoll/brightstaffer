from rest_framework import serializers
from brightStafferapp.models import Projects, Concept, Talent, Education, Company, TalentProject, TalentConcept, \
    TalentCompany, TalentEducation
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


class TalentEducationSerializer(serializers.ModelSerializer):

    class Meta:
        model = TalentEducation
        fields = ('talent', 'education', 'course', 'get_start_date', 'get_end_date')


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
        fields = ('talent', 'project', 'project_match', 'rank', 'stage','get_date_added','company_name')


class TalentConceptSerializer(serializers.ModelSerializer):
    talent = serializers.CharField()
    concept = serializers.CharField()

    class Meta:
        model = TalentConcept
        fields = ('talent', 'concept', 'match', 'get_date_created')


class TalentCompanySerializer(serializers.ModelSerializer):
    talent = serializers.CharField()
    company = serializers.CharField()
    years_of_experience = serializers.CharField()

    class Meta:
        model = TalentCompany
        fields = ('talent', 'company', 'designation', 'get_start_date', 'get_end_date','is_current','years_of_experience')


class TalentSerializer(serializers.ModelSerializer):
    talent_name = serializers.CharField()
    talent_education = TalentEducationSerializer(many=True)
    recruiter = serializers.CharField()
    talent_company = TalentCompanySerializer(many=True)
    talent_project = TalentProjectSerializer(many=True)
    talent_concepts = TalentConceptSerializer(many=True)

    class Meta:
        model = Talent
        fields = ('id', 'talent_name', 'designation', 'industry_focus','industry_focus_percentage', 'email_id', 'linkedin_url','contact_number',
                  'recruiter', 'get_date','current_location', 'talent_company',
                  'talent_education', 'talent_project', 'talent_concepts',)
