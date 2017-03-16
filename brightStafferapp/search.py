from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Text, Date
from elasticsearch.helpers import bulk
from elasticsearch import Elasticsearch
from . import models


connections.create_connection()


class BlogPostIndex(DocType):
    designation = Text()
    industry_focus = Date()
    linkedin_url = Text()
    rating = Text()


def bulk_indexing():
    BlogPostIndex.init()
    es = Elasticsearch()
    bulk(client=es, actions=(b.indexing() for b in models.Talent.objects.all().iterator()))