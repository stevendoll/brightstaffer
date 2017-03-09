import datetime
from haystack import indexes
from brightStafferapp.models import Talent, TalentProject
from datetime import datetime
from elasticsearch import Elasticsearch
from django.core import serializers
import json
import django.db.models.options as options


class TalentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    id = indexes.CharField(model_attr='id')
    talent_name = indexes.CharField(model_attr='talent_name')
    designation = indexes.CharField(model_attr='designation')
    industry_focus = indexes.CharField(model_attr='industry_focus')
    industry_focus_percentage = indexes.CharField(model_attr='industry_focus_percentage')
    linkedin_url = indexes.CharField(model_attr='linkedin_url')
    recruiter = indexes.CharField(model_attr='recruiter')
    contact = indexes.MultiValueField()
    email = indexes.MultiValueField()
    company = indexes.MultiValueField()
    education = indexes.MultiValueField()
    project = indexes.MultiValueField()
    concepts = indexes.MultiValueField()
    current_location = indexes.CharField(model_attr='current_location')
    rating = indexes.CharField(model_attr='rating')
    status = indexes.CharField(model_attr='status')
    create_date = indexes.DateTimeField(model_attr='create_date')
    suggestions = indexes.FacetCharField()

    def prepare(self, obj):
        prepared_data = super(TalentIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data

    def get_model(self):
        return Talent

    def prepare_email(self, obj):
        emails =[]
        for email in obj.talent_email.all():
            ema = dict()
            ema['talent'] = obj.talent_name
            ema['email'] = email.email
            ema['is_primary'] = email.is_primary
            emails.append(ema)
        return json.dumps(emails)

    def prepare_contact(self, obj):
        contacts =[]
        for contact in obj.talent_contact.all():
            cont = dict()
            cont['talent'] = obj.talent_name
            cont['contact'] = contact.contact
            cont['is_primary'] = contact.is_primary
            contacts.append(cont)
        return json.dumps(contacts)

    def prepare_education(self, obj):
        educations = []
        for education in obj.talent_education.all():
            edu = dict()
            edu['talent'] = obj.talent_name
            edu['education'] = education.education.name
            edu['course'] = education.course
            edu['start_date'] = str(education.start_date)
            edu['end_date'] = str(education.end_date)
            educations.append(edu)
        return json.dumps(educations)

    def prepare_company(self, obj):
        companies = []
        for company in obj.talent_company.all():
            comp = dict()
            comp['company'] = company.company.company_name
            comp['talent'] = obj.talent_name
            comp['start_date'] = str(company.start_date)
            comp['end_date'] = str(company.end_date)
            comp['designation'] = company.designation
            comp['is_current'] = company.is_current
            companies.append(comp)
        return json.dumps(companies)

    def prepare_project(self, obj):
        projects = []
        for project in obj.talent_project.all():
            proj = dict()
            proj['project'] = project.project.project_name
            proj['talent'] = obj.talent_name
            proj['project_match'] = project.project_match
            proj['rank'] = project.rank
            #proj['stage'] = project.stage
            proj['date_added'] = str(project.date_added)
            projects.append(proj)
        return json.dumps(projects)

    def prepare_recruiter(self, obj):
        return obj.recruiter.username

    def prepare_concepts(self, obj):
        concepts = []
        for concept in obj.talent_concepts.all():
            con = dict()
            con['talent'] = obj.talent_name
            con['concept'] = concept.concept.concept
            con['match'] = concept.match
            con['date_created'] = str(concept.date_created)
            concepts.append(con)
        return json.dumps(concepts)

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
