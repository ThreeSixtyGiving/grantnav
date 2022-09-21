from django.conf import settings
from collections import OrderedDict
import json
import copy
import warnings

by_publisher = OrderedDict()
by_identifier = {}

datasets = []

if settings.PROVENANCE_JSON:
    try:
        with open(settings.PROVENANCE_JSON) as fp:
            datasets = json.load(fp)

        for dataset in datasets:
            prefix = dataset['publisher']['prefix']
            if prefix not in by_publisher:
                by_publisher[prefix] = copy.deepcopy(dataset['publisher'])
                by_publisher[prefix]['datasets'] = []
            by_publisher[prefix]['datasets'].append(dataset)
            by_identifier[dataset.get('identifier')] = dataset
    except FileNotFoundError as e:
        warnings.warn(e)
else:
    warnings.warn("No publisher (provenance) data loaded")


def identifier_from_filename(filename):
    return filename.split('.')[0].split('/')[-1]
