import elasticsearch
from django.conf import settings


def get_es():
    return elasticsearch.Elasticsearch(hosts=[settings.ELASTICSEARCH_HOST])
