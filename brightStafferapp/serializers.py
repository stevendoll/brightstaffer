from rest_framework import serializers
from brightStafferapp.models import Projects, Concept, Talent, Education, Company, TalentProject, TalentConcept, \
    TalentCompany, TalentEducation,TalentContact, TalentEmail, TalentStage
from django.contrib.auth.models import User
import datetime


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
    education = serializers.CharField()
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
        fields = ('talent', 'project', 'stage','project_match', 'rank', 'get_date_added', 'company_name')


class TalentConceptSerializer(serializers.ModelSerializer):
    talent = serializers.CharField()
    concept = serializers.CharField()

    class Meta:
        model = TalentConcept
        fields = ('talent', 'concept', 'match', 'get_date_created')


class TalentEmailSerializer(serializers.ModelSerializer):
    talent = serializers.CharField()

    class Meta:
        model = TalentEmail
        fields = ('talent', 'email')


class TalentContactSerializer(serializers.ModelSerializer):
    talent = serializers.CharField()

    class Meta:
        model = TalentContact
        fields = ('talent', 'contact')


class TalentContactEmailSerializer(serializers.ModelSerializer):
    talent_contact = TalentContactSerializer(many=True)
    talent_email = TalentEmailSerializer(many=True)

    class Meta:
        model = Talent
        fields = ('id', 'talent_name', 'talent_contact', 'talent_email', )


class TalentProjectStageSerializer(serializers.ModelSerializer):
    talent = serializers.CharField()
    project = serializers.CharField()

    class Meta:
        model=TalentStage
        fields = ('id', 'talent', 'project', 'stage', 'details', 'notes', 'date_created', 'date_updated')


class TalentCompanySerializer(serializers.ModelSerializer):
    talent = serializers.CharField()
    company = serializers.CharField()
    years_of_experience = serializers.CharField()
    career_gap = serializers.SerializerMethodField()

    def get_career_gap(self, obj):
        check_date = obj.start_date
        previous_company = obj.talent.talent_company.filter(end_date__lt=check_date).order_by('start_date').last()
        if not previous_company:
            return 0
        date_diff = (obj.start_date - previous_company.end_date).days/365
        return date_diff

    class Meta:
        model = TalentCompany
        fields = ('talent', 'company', 'designation', 'get_start_date', 'get_end_date', 'is_current',
                  'years_of_experience', 'career_gap')


class TalentSerializer(serializers.ModelSerializer):
    talent_name = serializers.CharField()
    talent_education = TalentEducationSerializer(many=True)
    recruiter = serializers.CharField()
    talent_company = TalentCompanySerializer(many=True)
    talent_project = TalentProjectSerializer(many=True)
    talent_concepts = TalentConceptSerializer(many=True)
    talent_email = TalentEmailSerializer(many=True)
    talent_contact = TalentContactSerializer(many=True)

    class Meta:
        model = Talent
        fields = ('id', 'talent_name', 'designation', 'industry_focus', 'industry_focus_percentage', 'status',
        'rating', 'talent_email', 'talent_contact', 'linkedin_url', 'recruiter', 'get_date', 'current_location',
        'talent_company', 'talent_education', 'talent_project', 'talent_concepts')
