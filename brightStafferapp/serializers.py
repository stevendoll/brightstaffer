from rest_framework import serializers
from brightStafferapp.models import Projects, Concept, Talent, Education, Company, TalentProject, TalentConcept, \
    TalentCompany, TalentEducation,TalentContact, TalentEmail, TalentStage, FileUpload, TalentLocation
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
    talent = serializers.CharField()
    education = serializers.CharField()
    start_date = serializers.CharField(source='get_start_date')
    end_date = serializers.CharField(source='get_end_date')

    class Meta:
        model = TalentEducation
        fields = ('id', 'talent', 'education', 'course', 'start_date', 'end_date')


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'


class TalentProjectSerializer(serializers.ModelSerializer):
    project = serializers.CharField()
    talent = serializers.CharField()
    company_name = serializers.CharField()
    date_added = serializers.CharField(source='get_date_added')
    project_stage = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()

    def get_rank(self, obj):
        tp = TalentProject.objects.filter(project=obj.project).order_by('-project_match').values_list('project_match',
                                                                                                     flat=True)
        try:

            tp=sorted(list(set(list(tp))),reverse=True)
            rank = 0
            for i, t in enumerate(tp):
                if obj.project_match >= t:
                    return i+1
            return rank
        except:
            tp = TalentProject.objects.filter(project=obj.project).update(project_match=0)


    @staticmethod
    def get_project_stage(obj):
        stages = obj.project.talentstage_set.filter(talent=obj.talent).order_by('-id')
        if stages:
            return stages[0].stage
        return None

    class Meta:
        model = TalentProject
        fields = ('id', 'talent', 'project', 'project_match', 'rank',
                  'date_added', 'company_name', 'project_stage')


class TalentConceptSerializer(serializers.ModelSerializer):
    talent = serializers.CharField()
    concept = serializers.CharField()
    date_created = serializers.CharField(source='get_date_created')

    class Meta:
        model = TalentConcept
        fields = ('id', 'talent', 'concept', 'match', 'date_created')


class TalentEmailSerializer(serializers.ModelSerializer):
    talent = serializers.CharField()

    class Meta:
        model = TalentEmail
        fields = ('id', 'talent', 'email', 'is_primary')


class TalentContactSerializer(serializers.ModelSerializer):
    talent = serializers.CharField()

    class Meta:
        model = TalentContact
        fields = ('id', 'talent', 'contact', 'is_primary')


class TalentContactEmailSerializer(serializers.ModelSerializer):
    talent_contact = TalentContactSerializer(many=True)
    talent_email = TalentEmailSerializer(many=True)

    class Meta:
        model = Talent
        fields = ('id', 'talent_name', 'talent_contact', 'talent_email', )


class TalentProjectStageSerializer(serializers.ModelSerializer):
    talent = serializers.CharField()
    project = serializers.CharField()
    create_date=serializers.CharField(source='get_date_created')

    class Meta:
        model = TalentStage
        fields = ('id', 'talent', 'project', 'stage', 'details', 'notes', 'create_date', 'date_updated')


class TalentCompanySerializer(serializers.ModelSerializer):
    talent = serializers.CharField()
    company = serializers.CharField()
    years_of_experience = serializers.FloatField()
    career_gap = serializers.SerializerMethodField()
    start_date = serializers.CharField(source='get_start_date')
    end_date = serializers.CharField(source='get_end_date')

    def get_career_gap(self, obj):
        check_date = obj.start_date
        end_date = obj.end_date
        if check_date:
            previous_company = obj.talent.talent_company.filter(end_date__lte=check_date).order_by('start_date').last()
            #previous_company = obj.talent.talent_company.filter(start_date__lte=check_date).order_by('start_date').last()
            if not previous_company:
                return 0
            # if previous_company.end_date is None:
            #     previous_company.end_date = datetime.date()
            #     print (previous_company.end_date)
            date_diff = (obj.start_date - previous_company.end_date).days/365
            return date_diff

    class Meta:
        model = TalentCompany
        fields = ('id', 'talent', 'company', 'designation', 'start_date', 'end_date', 'is_current',
                  'years_of_experience', 'career_gap')


class TalentStageSerializer(serializers.ModelSerializer):
    talent = serializers.CharField()
    create_date = serializers.CharField(source='get_date_created')
    date_updated = serializers.CharField(source='get_date_updated')
    project = serializers.CharField()
    class Meta:
        model = TalentStage
        fields = ('id', 'talent', 'project', 'stage', 'details', 'notes', 'create_date', 'date_updated')


class FileStageSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    file = serializers.FileField()
    file_name = serializers.CharField()
    user = serializers.CharField()
    talent = serializers.CharField()
    create_date = serializers.CharField(source='get_date_created')
    class Meta:
        model = FileUpload
        fields = ('id', 'name', 'file','file_name', 'user', 'talent','create_date')


class TalentLocationSerializer(serializers.ModelSerializer):
    city = serializers.CharField()
    state = serializers.CharField()
    country = serializers.CharField()
    talent = serializers.CharField()
    #create_date = serializers.CharField(source='get_date_created')
    class Meta:
        model = TalentLocation
        fields = ('id', 'city', 'state', 'country', 'talent')


class TalentSerializer(serializers.ModelSerializer):
    talent_name = serializers.CharField()
    #current_location = serializers.SerializerMethodField()
    talent_education = TalentEducationSerializer(many=True)
    recruiter = serializers.CharField()
    request_by = serializers.CharField()
    create_date = serializers.CharField(source='get_date')
    update_date = serializers.CharField(source='get_update_date')
    activation_date = serializers.CharField(source='get_activation_date')
    talent_company = TalentCompanySerializer(many=True)
    talent_project = TalentProjectSerializer(many=True)
    talent_concepts = TalentConceptSerializer(many=True)
    talent_email = TalentEmailSerializer(many=True)
    talent_contact = TalentContactSerializer(many=True)
    talent_stages = TalentStageSerializer(many=True)
    current_location = TalentLocationSerializer(many=True)
    file_upload = FileStageSerializer(many=True)

    # def get_current_location(self, obj):
    #     if obj.current_location.all():
    #         return str(obj.current_location.all()[0])
    #     else:
    #         return ''

    class Meta:
        model = Talent
        fields = ('id', 'image', 'talent_name','current_location', 'designation', 'industry_focus', 'activation_date',
                  'industry_focus_percentage',
                  'status', 'rating', 'talent_email', 'talent_stages', 'file_upload', 'talent_contact',
                  'linkedin_url', 'recruiter',
                  'create_date', 'update_date','talent_company', 'talent_education', 'talent_project','request_by',
                  'talent_concepts')
