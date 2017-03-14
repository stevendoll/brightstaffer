import datetime
from haystack import indexes
from brightStafferapp.models import Talent, TalentProject
from datetime import datetime
from elasticsearch import Elasticsearch
from django.core import serializers
import json
import django.db.models.options as options


class TalentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=False)
    id = indexes.CharField(model_attr='id')
    talent_name = indexes.CharField(model_attr='talent_name')
    designation = indexes.CharField(model_attr='designation')
    industry_focus = indexes.CharField(model_attr='industry_focus')
    industry_focus_percentage = indexes.CharField(model_attr='industry_focus_percentage')
    linkedin_url = indexes.CharField(model_attr='linkedin_url')
    recruiter = indexes.CharField(model_attr='recruiter')
    talent_contact = indexes.MultiValueField()
    talent_email = indexes.MultiValueField()
    talent_company = indexes.MultiValueField()
    talent_education = indexes.MultiValueField()
    talent_project = indexes.MultiValueField()
    talent_concepts = indexes.MultiValueField()
    talent_stages = indexes.MultiValueField()
    current_location = indexes.CharField(model_attr='current_location')
    rating = indexes.CharField(model_attr='rating')
    status = indexes.CharField(model_attr='status')
    create_date = indexes.DateTimeField(model_attr='create_date')
    # suggestions = indexes.FacetCharField()

    # def prepare(self, obj):
    #     prepared_data = super(TalentIndex, self).prepare(obj)
    #     prepared_data['suggestions'] = prepared_data['text']
    #     return prepared_data

    def get_model(self):
        return Talent

    def prepare_create_date(self, obj):
        return str(obj.get_date)

    def prepare_talent_stages(self, obj):
        stages = []
        for stage in obj.talent_stages.all():
            sta = dict()
            sta['talent'] = obj.talent_name
            sta['project'] = stage.project.project_name
            sta['details'] = stage.details
            sta['notes'] = stage.notes
            sta['date_created'] = str(stage.get_date_created)
            sta['date_updated'] = str(stage.get_date_updated)
            stages.append(sta)
        return stages

    def prepare_talent_email(self, obj):
        emails =[]
        for email in obj.talent_email.all():
            ema = dict()
            ema['talent'] = obj.talent_name
            ema['email'] = email.email
            ema['is_primary'] = email.is_primary
            emails.append(ema)
        return emails

    def prepare_talent_contact(self, obj):
        contacts =[]
        for contact in obj.talent_contact.all():
            cont = dict()
            cont['talent'] = obj.talent_name
            cont['contact'] = contact.contact
            cont['is_primary'] = contact.is_primary
            contacts.append(cont)
        return contacts

    def prepare_talent_education(self, obj):
        educations = []
        for education in obj.talent_education.all():
            edu = dict()
            edu['talent'] = obj.talent_name
            edu['education'] = education.education.name
            edu['course'] = education.course
            edu['start_date'] = str(education.get_start_date)
            edu['end_date'] = str(education.get_end_date)
            educations.append(edu)
        return educations

    def prepare_talent_company(self, obj):
        companies = []
        for company in obj.talent_company.all():
            comp = dict()
            comp['company'] = company.company.company_name
            comp['talent'] = obj.talent_name
            comp['start_date'] = str(company.get_start_date)
            comp['end_date'] = str(company.get_end_date)
            comp['designation'] = company.designation
            comp['is_current'] = company.is_current
            comp['years_of_experience'] = company.years_of_experience
            comp['career_gap'] = self.get_career_gap(company)
            companies.append(comp)
        return companies

    def get_career_gap(self, obj):
        check_date = obj.start_date
        previous_company = obj.talent.talent_company.filter(end_date__lt=check_date).order_by('start_date').last()
        if not previous_company:
            return 0
        date_diff = (obj.start_date - previous_company.end_date).days/365
        return date_diff

    def prepare_talent_project(self, obj):
        projects = []
        for project in obj.talent_project.all():
            proj = dict()
            proj['project'] = project.project.project_name
            proj['talent'] = obj.talent_name
            proj['project_match'] = project.project_match
            proj['rank'] = project.rank
            proj['project_stage'] = self.get_project_stage(project)
            proj['date_added'] = str(project.get_date_added)
            proj['company_name'] = project.company_name
            projects.append(proj)
        return projects

    def get_project_stage(self, obj):
        stages = obj.project.talentstage_set.filter(talent=obj.talent).order_by('-date_created')
        if stages:
            return stages[0].stage
        return None

    def prepare_recruiter(self, obj):
        return obj.recruiter.username

    def prepare_talent_concepts(self, obj):
        concepts = []
        for concept in obj.talent_concepts.all():
            con = dict()
            con['talent'] = obj.talent_name
            con['concept'] = concept.concept.concept
            con['match'] = concept.match
            con['date_created'] = str(concept.get_date_created)
            concepts.append(con)
        return concepts

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
