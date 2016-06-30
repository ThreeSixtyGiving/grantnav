from django.conf import settings
import json

by_publisher = {}

if settings.PROVENANCE_JSON:
    with open(settings.PROVENANCE_JSON) as fp:
        provenance = json.load(fp)

    for dataset in provenance:
        prefix = dataset['publisher']['prefix']
        if prefix not in by_publisher:
            by_publisher[prefix] = dataset['publisher']
            by_publisher[prefix]['datasets'] = []
        by_publisher[prefix]['datasets'].append(dataset)
