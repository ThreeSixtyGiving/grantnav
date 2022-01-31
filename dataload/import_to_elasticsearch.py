#!/usr/bin/env python3
import json
import argparse
import flattentool
import shutil
import uuid
import tempfile
import os
import csv
from pprint import pprint
import elasticsearch.helpers
import requests
import time
import ijson
import dateutil.parser as date_parser


ES_INDEX = os.environ.get("ES_INDEX", "threesixtygiving")
ELASTICSEARCH_HOST = os.environ.get("ELASTICSEARCH_HOST", "localhost")

id_name_org_mappings = {"fundingOrganization": {}, "recipientOrganization": {}}
name_duplicates = [["file_name", "org_type", "org_id", "first_name", "duplicate_name"]]
bad_org_ids = []

postcode_to_area = {}
district_code_to_area = {}
ward_code_to_area = {}
district_name_to_code = {}

current_dir = os.path.dirname(os.path.realpath(__file__))


def convert_spreadsheet(file_path, file_type, tmp_dir):
    #file_type = file_name.split('.')[-1]
    encoding = 'utf-8'
    converted_path = os.path.join(tmp_dir, 'output.json')
    if file_type == 'csv':
        destination = os.path.join(tmp_dir, 'grants.csv')
        shutil.copy(file_path, destination)
        try:
            with open(destination, encoding='utf-8') as main_sheet_file:
                main_sheet_file.read()
        except UnicodeDecodeError:
            try:
                with open(destination, encoding='cp1252') as main_sheet_file:
                    main_sheet_file.read()
                encoding = 'cp1252'
            except UnicodeDecodeError:
                encoding = 'latin_1'
        input_name = tmp_dir
    else:
        input_name = file_path
    try:
        flattentool.unflatten(
            input_name,
            output_name=converted_path,
            input_format=file_type,
            main_sheet_name='grants',
            root_list_path='grants',
            root_id='',
            schema='https://raw.githubusercontent.com/ThreeSixtyGiving/standard/master/schema/360-giving-schema.json',
            convert_titles=True,
            encoding=encoding
        )
    except Exception:
        print("Unflattening failed for file {}".format(file_path))
        raise

# curl http://test-360giving.pantheon.io/api/3/action/current_package_list_with_resources | grep -Eo '[^"]+\.json' | sed 's/\\\//\//g' | while read url; do wget "$url"; done


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
                    }
                }
            },
            "currencies": {
                "type": "keyword"
            },
            "organizationName": {
                "type": "text",
                "analyzer": "english_with_folding"
            },
            "orgIDs": {
                "type": "keyword"
            },
            "grants": {
                "type": "double"
            },
            "maxAwardDate": {
                "type": "date",
                "ignore_malformed": True
            },
            "minAwardDate": {
                "type": "date",
                "ignore_malformed": True
            },
            "currencyGrants": {
                "dynamic": True,
                "properties": {}
            },
            "currencyTotal": {
                "dynamic": True,
                "properties": {}
            },
            "currencyMaxAmount": {
                "dynamic": True,
                "properties": {}
            },
            "currencyMinAmount": {
                "dynamic": True,
                "properties": {}
            },
            "currencyAvgAmount": {
                "dynamic": True,
                "properties": {}
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


def import_to_elasticsearch(files, clean, recipients, funders):

    es = elasticsearch.Elasticsearch(hosts=[ELASTICSEARCH_HOST])

    # Delete the index
    if clean:
        result = es.indices.delete(index=ES_INDEX, ignore=[404])
        pprint(result)

    maybe_create_index()

    time.sleep(1)

    def org_generator(filename, data_type):
        with open(filename) as f:
            for obj in ijson.items(f, '', multiple_values=True):
                obj['dataType'] = data_type
                obj['_id'] = str(uuid.uuid4())
                obj['_index'] = ES_INDEX
                yield obj

    if recipients:
        result = elasticsearch.helpers.bulk(es, org_generator(recipients, 'recipient'), raise_on_error=False, max_retries=10, initial_backoff=5)
        print(result)
    if funders:
        result = elasticsearch.helpers.bulk(es, org_generator(funders, 'funder'), raise_on_error=False, max_retries=10, initial_backoff=5)
        print(result)

    with open(os.path.join(current_dir, 'charity_names.json')) as fd:
        charity_names = json.load(fd)
    id_name_org_mappings["recipientOrganization"].update(charity_names)

    with open(os.path.join(current_dir, 'primary_funding_org_name.json')) as fd:
        funding_org_name = json.load(fd)
    id_name_org_mappings["fundingOrganization"].update(funding_org_name)

    for file_name in files:
        tmp_dir = tempfile.mkdtemp()
        if file_name.startswith('http'):
            content = requests.get(file_name).content
            new_filename = file_name.split('/')[-1].split('?')[0]
            downloaded_filename = os.path.join(tmp_dir, new_filename)
            with open(downloaded_filename, 'wb+') as downloaded_file:
                downloaded_file.write(content)
            file_name = downloaded_filename

        file_type = file_name.split('.')[-1]

        if file_type == 'json':
            json_file_name = file_name
        elif file_type in ('csv', 'xlsx'):
            json_file_name = os.path.join(tmp_dir, 'output.json')
            convert_spreadsheet(file_name, file_type, tmp_dir)
        elif file_type in ('report'):
            continue
        else:
            print('unimportable file {} (bad) file type'.format(file_name))
            continue

        def grant_generator():
            """ Add / Update GrantNav specific optimisation fields """

            with open(json_file_name) as fp:
                stream = ijson.items(fp, 'grants.item')
                for grant in stream:
                    grant['filename'] = file_name.strip('./')
                    grant['_id'] = str(uuid.uuid4())
                    grant['_index'] = ES_INDEX
                    grant['dataType'] = 'grant'

                    # grant.fundingOrganization.id_and_name
                    update_doc_with_org_mappings(grant, "fundingOrganization", file_name)
                    # grant.recipientOrganization.id_and_name
                    update_doc_with_org_mappings(grant, "recipientOrganization", file_name)
                    # grant.title_and_description
                    update_doc_with_title_and_description(grant)
                    # grant.grantProgramme.title_keyword
                    update_doc_with_grantprogramme_title_keyword(grant)
                    # grant.actualDates.N.[start,end]DateDateOnly
                    # grant.plannedDates.N.[start,end]DateDateOnly
                    update_doc_with_dateonly_fields(grant)
                    # grant.currency
                    update_doc_with_currency_upper_case(grant)

                    yield grant

        pprint(file_name)
        result = elasticsearch.helpers.bulk(es, grant_generator(), raise_on_error=False, max_retries=10, initial_backoff=5)
        pprint(result)

        shutil.rmtree(tmp_dir)


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


def get_canonical_name(grant, org_key):
    additional_data = grant.get('additional_data')
    if additional_data:
        canonical_org = additional_data.get('{}Canonical'.format(org_key))
        if canonical_org:
            return canonical_org.get('name')

    return None


def update_doc_with_grantprogramme_title_keyword(grant):
    if 'grantProgramme' in grant and isinstance(grant['grantProgramme'], list):
        for grant_programme in grant['grantProgramme']:
            if 'title' in grant_programme:
                grant_programme['title_keyword'] = grant_programme['title']


def update_doc_with_org_mappings(grant, org_key, file_name):
    mapping = id_name_org_mappings[org_key]
    orgs = grant.get(org_key, [])
    for org in orgs:
        org_id, org_name = org.get('id'), org.get('name')
        name = get_canonical_name(grant, org_key)

        if not name:
            name = org_name
        if not org_name:
            name = org_id
        if not org_id:
            return

        if '/' in org_id:
            bad_org_ids.append([file_name, org_key, org_id])

        found_name = mapping.get(org_id)
        if found_name:
            if found_name != name:
                name_duplicates.append([file_name, org_key, org_id, found_name, name])
            if found_name != org_name and name != org_name:
                name_duplicates.append([file_name, org_key, org_id, found_name, org_name])
        else:
            mapping[org_id] = name
            found_name = name
        org["id_and_name"] = json.dumps([found_name, org_id])


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
    parser.add_argument('--reports', help='Generate reports of differing names and bad organisation IDs.', action='store_true')
    parser.add_argument('--recipients', help='recipients file')
    parser.add_argument('--funders', help='funders file')
    parser.add_argument('files', help='files to import', nargs='*')
    args = parser.parse_args()

    import_to_elasticsearch(args.files, args.clean, args.recipients, args.funders)

    if args.reports:
        with open("differing_names.csv.report", "w+") as differing_names_file:
            csv_writer = csv.writer(differing_names_file)
            csv_writer.writerows(name_duplicates)
        with open("bad_org_ids.csv.report", "w+") as bad_org_ids_file:
            csv_writer = csv.writer(bad_org_ids_file)
            csv_writer.writerows(bad_org_ids)
