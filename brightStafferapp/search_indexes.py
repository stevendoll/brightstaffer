import datetime
from haystack import indexes
from brightStafferapp.models import Talent, TalentProject
from datetime import datetime
from elasticsearch import Elasticsearch
from django.core import serializers


class ProjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    project_match = indexes.CharField(model_attr='project_match')
    rank = indexes.CharField(model_attr='rank')

    def get_model(self):
        return TalentProject


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
    project = ProjectIndex()
    concepts = indexes.MultiValueField()
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
    #
    # def prepare_company(self, obj):
    #     return [category.id for category in obj.category_set.active().order_by('-created')]

    def format_company(self, company):
        company_dict = dict()
        company_dict['name'] = company.company.company_name
        return company.company.company_name
    #
    def prepare_project(self, obj):
        return [proj.project.project_name for proj in obj.talent_project.all()]

    def prepare_recruiter(self, obj):
        return obj.recruiter.username

    def prepare_concepts(self, obj):
        return [concept.concept for concept in obj.concepts.all()]

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()


# es = Elasticsearch()
#
# doc = {
#     'author': 'kimchy',
#     'text': 'Elasticsearch: cool. bonsai cool.',
#     'timestamp': datetime.now(),
# }
# res = es.index(index="test1", doc_type='tweet', id=1, body=doc)
# print(res['created'])
#
# res = es.index(index="test2", doc_type='tweet', id=1, body=doc)
# print(res['created'])
#
# res = es.get(index="test-index", doc_type='tweet', id=1)
# print(res['_source'])
#
# es.indices.refresh(index="test-index")
#
# res = es.search(index="test-index", body={"query": {"match_all": {}}})
# print("Got %d Hits:" % res['hits']['total'])
# for hit in res['hits']['hits']:
#     print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])