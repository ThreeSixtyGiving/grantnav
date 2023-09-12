#!/usr/bin/env python3
import argparse
import json
import shutil
import uuid
import tempfile
import os
from pprint import pprint
import warnings
import elasticsearch.helpers
import time
import ijson
import dateutil.parser as date_parser

import sys

from django.core.cache import cache
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "grantnav.settings")


sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from grantnav.frontend.org_utils import new_ordered_names, new_org_ids, get_org, OrgNotFoundError # noqai

django.setup()

ES_INDEX = os.environ.get("ES_INDEX", "threesixtygiving")
ELASTICSEARCH_HOST = os.environ.get("ELASTICSEARCH_HOST", "localhost")


def maybe_create_index(index_name=ES_INDEX):
    """ Creates a new ES index based on value of ES_INDEX
    unless it already exists """
    es = elasticsearch.Elasticsearch(hosts=[ELASTICSEARCH_HOST])

    # Add the extra mapping info we want
    # (the rest will be auto inferred from the data we feed in)
    #
    # See issue #503 for why we do this for a non-standard field (Reference)
    # Fields must appear here to be indexed
    mappings = {
        "date_detection": False,
        "numeric_detection": False,
        "dynamic": False,

        "properties": {
            "dataType": {"type": "keyword"},
            "id": {"type": "keyword"},
            "filename": {"type": "keyword"},
            "title": {
                "type": "text", "analyzer": "english_with_folding"
            },
            "description": {
                "type": "text", "analyzer": "english_with_folding"
            },
            "currency": {"type": "keyword"},
            "Reference": {"type": "keyword"},
            "title_and_description": {"type": "text", "analyzer": "english_with_folding"},
            "amountAppliedFor": {"type": "double"},
            "amountAwarded": {"type": "double"},
            "amountDisbursed": {"type": "double"},
            "awardDate": {
                "type": "date",
                "ignore_malformed": True
            },
            "dateModified": {"type": "keyword"},
            "plannedDates": {
                "properties": {
                    "startDate": {"type": "keyword"},
                    "endDate": {"type": "keyword"},
                    "duration": {"type": "text"}
                }
            },
            "recipientOrganization": {
                "properties": {
                    "addressLocality": {
                        "type": "keyword"
                    },
                    "charityNumber": {
                        "type": "keyword"
                    },
                    "companyNumber": {
                        "type": "keyword"
                    },
                    "id": {
                        "type": "keyword"
                    },
                    "url": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text", "analyzer": "english_with_folding"
                    },
                    "streetAddress": {
                        "type": "text", "analyzer": "english_with_folding"
                    },
                    "description": {
                        "type": "text", "analyzer": "english_with_folding"
                    },
                    "id_and_name": {
                        "type": "keyword"
                    }
                }
            },
            "recipientIndividual": {
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                }
            },
            "toIndividualsDetails": {
                "properties": {
                    "primaryGrantReason": {
                        "type": "keyword"
                    },
                    "secondaryGrantReason": {
                        "type": "keyword"
                    },
                    "grantPurpose": {
                        "type": "keyword"
                    },
                }
            },
            "fundingOrganization": {
                "properties": {
                    "addressLocality": {
                        "type": "keyword"
                    },
                    "charityNumber": {
                        "type": "keyword"
                    },
                    "companyNumber": {
                        "type": "keyword"
                    },
                    "id": {
                        "type": "keyword"
                    },
                    "url": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text", "analyzer": "english_with_folding"
                    },
                    "description": {
                        "type": "text", "analyzer": "english_with_folding"
                    },
                    "streetAddress": {
                        "type": "text", "analyzer": "english_with_folding"
                    },
                    "department": {
                        "type": "text", "analyzer": "english_with_folding"
                    },
                    "id_and_name": {
                        "type": "keyword"
                    }
                }
            },
            "beneficiaryLocation": {
                "properties": {
                    "geographic code (from GIFTS)": {"type": "text"}
                }
            },
            "grantProgramme": {
                "properties": {
                    # Include title as keyword and text, so that both facets
                    # and free text search work
                    "title_keyword": {
                        "type": "keyword"
                    },
                    "title": {
                        "type": "text", "analyzer": "english_with_folding"
                    },
                    "description": {
                        "type": "text", "analyzer": "english_with_folding"
                    },
                }
            },
            "fundingType": {
                "properties": {
                    "title": {
                        "type": "text", "analyzer": "english_with_folding"
                    },
                }
            },
            "classifications": {
                "properties": {
                    "title": {
                        "type": "text", "analyzer": "english_with_folding"
                    },
                }
            },
            "regrantType": {"type": "keyword"},
            "simple_grant_type": {"type": "keyword"},

            "additional_data": {
                "properties": {
                    "recipientDistrictGeoCode": {
                        "type": "keyword"
                    },
                    "recipientDistrictName": {
                        "type": "keyword"
                    },
                    "recipientRegionName": {
                        "type": "keyword"
                    },
                    "recipientWardName": {
                        "type": "keyword"
                    },
                    "TSGFundingOrgType": {
                        "type": "keyword"
                    },
                    "TSGRecipientType": {
                        "type": "keyword"
                    },
                    "codeListLookup": {
                        "properties": {
                            "toIndividualsDetails": {
                                "properties": {
                                    "primaryGrantReason": {
                                        "type": "keyword"
                                    },
                                    "secondaryGrantReason": {
                                        "type": "keyword"
                                    },
                                    "grantPurpose": {
                                        "type": "keyword"
                                    },
                                }
                            },
                            "regrantType": {
                                "type": "keyword",
                            }
                        }
                    },
                    "recipientLocation": {
                        "type": "text"
                    },
                    "recipientOrganizationLocation": {
                        "properties": {
                            "rgn": {
                                "type": "keyword"
                            },
                            "ctry": {
                                "type": "keyword"
                            }
                        }
                    },
                    "GNCanonicalRecipientOrgId": {
                        "type": "keyword"
                    },
                    "GNCanonicalFundingOrgId": {
                        "type": "keyword"
                    },
                    "recipientOrgInfos": {
                        "properties": {
                            "organisationTypePrimary": {
                                "type": "keyword"
                            }
                        }
                    }
                }
            },
            # Additional funding/recipient organisation mappings
            "organizationName": {
                "type": "text",
                "analyzer": "english_with_folding"
            },
            "orgIDs": {
                "type": "keyword"
            },
            "aggregate": {
                "properties": {
                    "grants": {"type": "double"},
                    "maxAwardDate": {
                        "type": "date",
                        "ignore_malformed": True
                    },
                    "minAwardDate": {
                        "type": "date",
                        "ignore_malformed": True
                    },
                    "currencies": {
                        "properties": {
                            # Currently we do things like order-by on GBP
                            "GBP": {
                                "properties": {
                                    "avg": {"type": "double"},
                                    "total": {"type": "double"},
                                }
                            }

                        }
                    }
                }
            },
        }
    }

    settings = {
        "max_result_window": 500000,
        "analysis": {
            "analyzer": {
                # Based on the english analyzer decribed at
                # https://www.elastic.co/guide/en/elasticsearch/reference/2.4/analysis-lang-analyzer.html#english-analyzer
                "english_with_folding": {
                    "tokenizer": "standard",
                    "filter": [
                        # asciifolding not in the standard english analyzer.
                        "asciifolding",
                        "english_possessive_stemmer",
                        "lowercase",
                        "english_stop",
                        "english_stemmer",
                    ]
                }
            },
            "filter": {
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                }
            }
        },
    }

    # Create it
    result = es.indices.create(index=index_name, body={"mappings": mappings, "settings": settings}, ignore=[400])
    if 'error' in result:
        if 'already exists' in result['error']['reason']:
            print('Updating existing index')
        else:
            pprint(result)
            raise Exception("Creating index failed")
    else:
        pprint(result)

    # set cluster level settings

    result = es.cluster.put_settings(body={"persistent": {
        "search.max_buckets": "500000"
    }})


def import_to_elasticsearch(files, clean, recipients=None, funders=None):

    es = elasticsearch.Elasticsearch(hosts=[ELASTICSEARCH_HOST])
    # Clear any query caches
    print("clearing caches")
    cache.clear()

    # Delete the index
    if clean:
        result = es.indices.delete(index=ES_INDEX, ignore=[404])
        pprint(result)

    maybe_create_index()
    # Allow the server to settle
    time.sleep(1)

    # Load the organisations data
    def org_generator(filename, data_type):
        with open(filename) as f:
            for obj in ijson.items(f, '', multiple_values=True):
                obj['dataType'] = data_type
                obj['_id'] = str(uuid.uuid4())
                obj['_index'] = ES_INDEX
                obj['currency'] = list(obj["aggregate"]["currencies"].keys())
                obj['organizationName'] = " ".join(new_ordered_names(obj))
                obj['orgIDs'] = new_org_ids(obj)
                yield obj

    if recipients:
        result = elasticsearch.helpers.bulk(es, org_generator(recipients, 'recipient'), raise_on_error=False, max_retries=10, initial_backoff=5)
        print(result)
    if funders:
        result = elasticsearch.helpers.bulk(es, org_generator(funders, 'funder'), raise_on_error=False, max_retries=10, initial_backoff=5)
        print(result)

    # Load the grants data
    for grants_file_path in files:
        tmp_dir = tempfile.mkdtemp()

        file_type = grants_file_path.split('.')[-1]

        if file_type != 'json':
            print('unimportable file {} (bad) file type'.format(grants_file_path))
            continue

        def grant_generator():
            """ Add / Update GrantNav specific optimisation fields """

            with open(grants_file_path) as fp:
                stream = ijson.items(fp, 'grants.item')
                for grant in stream:
                    grant['filename'] = os.path.basename(grants_file_path)
                    grant['_id'] = str(uuid.uuid4())
                    grant['_index'] = ES_INDEX
                    grant['dataType'] = 'grant'

                    # We use additional_data extensively in GN if it is missing things
                    # might not work as expected
                    try:
                        if type(grant["additional_data"]) != dict:
                            raise TypeError("additional_data not a dictionary")
                    except (TypeError, KeyError):
                        warnings.warn("No additional_data block for grant: %s" % grant["id"])
                        # initialise the dictionary for our own additional data
                        grant["additional_data"] = {}

                    # Search helper fields:

                    # grant.fundingOrganization.id_and_name
                    # grant.recipientOrganization.id_and_name
                    # grant.additional_data.GNCanonicalRecipientOrgName
                    # grant.additional_data.GNCanonicalFundingOrgName
                    update_doc_with_canonical_orgs(grant)
                    # grant.title_and_description
                    update_doc_with_title_and_description(grant)
                    # grant.grantProgramme.title_keyword
                    update_doc_with_grantprogramme_title_keyword(grant)
                    # grant.actualDates.N.[start,end]DateDateOnly
                    # grant.plannedDates.N.[start,end]DateDateOnly
                    update_doc_with_dateonly_fields(grant)
                    # grant.currency
                    update_doc_with_currency_upper_case(grant)
                    # grant.simple_grant_type
                    update_doc_with_simple_grant_type(grant)
                    yield grant

        pprint(grants_file_path)
        result = elasticsearch.helpers.bulk(es, grant_generator(), raise_on_error=False, max_retries=10, initial_backoff=5)
        pprint(result)

        shutil.rmtree(tmp_dir)

    # Clear any query caches
    cache.clear()


def update_doc_with_canonical_orgs(grant):
    """ Uses our org data from the datastore to add canonical org data to additional_data"""
    # RecipientOrganisation
    if grant_recipient_org := grant.get("recipientOrganization", [""])[0]:
        try:
            recipient_org = get_org(grant_recipient_org["id"], "recipient")
            grant["additional_data"]["GNCanonicalRecipientOrgName"] = new_ordered_names(recipient_org)[0]
            grant["additional_data"]["GNCanonicalRecipientOrgId"] = new_org_ids(recipient_org)[0]
        except OrgNotFoundError:
            grant["additional_data"]["GNCanonicalRecipientOrgName"] = grant["recipientOrganization"][0]["name"]
            grant["additional_data"]["GNCanonicalRecipientOrgId"] = grant["recipientOrganization"][0]["id"]

        # Legacy search helper field used for *_datatables
        grant["recipientOrganization"][0]["id_and_name"] = json.dumps(
            [grant["additional_data"]["GNCanonicalRecipientOrgName"],
            grant["additional_data"]["GNCanonicalRecipientOrgId"]]
        )

    # FundingOrganisation
    try:
        funding_org = get_org(grant["fundingOrganization"][0]["id"], "funder")
        grant["additional_data"]["GNCanonicalFundingOrgName"] = new_ordered_names(funding_org)[0]
        grant["additional_data"]["GNCanonicalFundingOrgId"] = new_org_ids(funding_org)[0]
    except OrgNotFoundError:
        grant["additional_data"]["GNCanonicalFundingOrgName"] = grant["fundingOrganization"][0]["name"]
        grant["additional_data"]["GNCanonicalFundingOrgId"] = grant["fundingOrganization"][0]["id"]

    # Legacy search helper field used for *_datatables
    grant["fundingOrganization"][0]["id_and_name"] = json.dumps(
        [grant["additional_data"]["GNCanonicalFundingOrgName"],
        grant["additional_data"]["GNCanonicalFundingOrgId"]])


def update_doc_with_simple_grant_type(grant):
    grant["simple_grant_type"] = "For regrant" if grant.get("regrantType") else "Direct grant"


def update_doc_with_currency_upper_case(grant):
    currency = grant.get('currency')
    if currency:
        grant['currency'] = currency.upper()


def update_doc_with_title_and_description(grant):
    """
    Update ElasticSearch with the new key 'title_and_description'.
    """
    description = grant.get('description') if grant.get('description') else ''
    title = grant.get('title') if grant.get('title') else ''
    grant['title_and_description'] = title + ' ' + description


def update_doc_with_grantprogramme_title_keyword(grant):
    if 'grantProgramme' in grant and isinstance(grant['grantProgramme'], list):
        for grant_programme in grant['grantProgramme']:
            if 'title' in grant_programme:
                grant_programme['title_keyword'] = grant_programme['title']


def update_doc_with_dateonly_fields(grant):
    """
    If possible parse the date to only show the date part
    rather than the full ISO date
    """
    def add_dateonly(parent, key):
        try:
            datetime = date_parser.parse(parent.get(key))
            parent[key + 'DateOnly'] = datetime.date().isoformat()
        except (ValueError, TypeError):
            parent[key + 'DateOnly'] = parent.get(key)

    add_dateonly(grant, 'awardDate')

    for dates in grant.get('plannedDates', []) + grant.get('actualDates', []):
        add_dateonly(dates, 'startDate')
        add_dateonly(dates, 'endDate')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import 360 files in a directory to elasticsearch')
    parser.add_argument('--clean', help='Delete existing data before import', action='store_true')
    parser.add_argument('--recipients', help='recipients file')
    parser.add_argument('--funders', help='funders file')
    parser.add_argument('files', help='files to import', nargs='*')
    args = parser.parse_args()

    import_to_elasticsearch(args.files, args.clean, args.recipients, args.funders)