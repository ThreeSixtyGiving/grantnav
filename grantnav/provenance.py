from django.conf import settings
from collections import OrderedDict
import json

by_publisher = OrderedDict()
by_identifier = {}

datasets = []

if settings.PROVENANCE_JSON:
    with open(settings.PROVENANCE_JSON) as fp:
        datasets = json.load(fp)

    for dataset in datasets:
        prefix = dataset['publisher']['prefix']
        if prefix not in by_publisher:
            by_publisher[prefix] = dataset['publisher']
            by_publisher[prefix]['datasets'] = []
        by_publisher[prefix]['datasets'].append(dataset)
        by_identifier[dataset.get('identifier')] = dataset


def identifier_from_filename(filename):
    return filename.split('.')[0].split('/')[-1]
