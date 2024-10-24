import json
import time

import pytest
import os

from dataload.import_to_elasticsearch import import_to_elasticsearch
from grantnav.frontend.search_helpers import get_pagination
from grantnav.frontend.views import BASIC_QUERY, create_parameters_from_json_query
from django.test.client import RequestFactory
from django.urls import reverse_lazy


prefix = f"{os.path.dirname(__file__)}/../../dataload/test_data/"


@pytest.fixture(scope="module")
def dataload():
    import_to_elasticsearch(
        [
            prefix + 'a002400000KeYdsAAF.json',
            prefix + 'grantnav-20180903134856.json',
            prefix + 'a002400000nO46WAAS.json'
        ],
        clean=True,
        funders=os.path.join(prefix, "funders.jl"),
        recipients=os.path.join(prefix, "recipients.jl")
    )
    #elastic search needs some time to commit its data
    time.sleep(2)
    # Recreate this test dataload:
    # $ ES_INDEX=test ./dataload/import_to_elasticsearch.py ./dataload/test_data/a002400000KeYdsAAF.json ./dataload/test_data/grantnav-20180903134856.json ./dataload/test_data/a002400000nO46WAAS.json --funders ./dataload/test_data/funders.jl --recipients ./dataload/test_data/recipients.jl --clean


@pytest.fixture(scope="function")
def provenance_dataload(dataload, settings, tmpdir):
    settings.PROVENANCE_JSON = os.path.join(prefix, "data.json")


@pytest.mark.parametrize(('expected_text'), [
    ('GrantNav'),
    ('Search'),
    ('Help'),
    ])
def test_home(provenance_dataload, client, expected_text):
    response = client.get('/')
    assert expected_text in str(response.content)
    assert "grant-making" not in str(response.content)


def test_prometheus(provenance_dataload, client):
    assert "total_grants 1254.0" in str(client.get("/prometheus/metrics").content)


@pytest.mark.parametrize(('search_query', 'expected_grants'), [
    ("gardens+AND+fundingOrganization.id:GB-CHC-1156077", 7),
    ("E09000033+AND+fundingOrganization.id:GB-CHC-1156077", 19),
    ("E10000023+AND+fundingOrganization.id:GB-CHC-1156077", 0),
    ("Esmee", 5),
    ("Esmée", 5),
    ("Esmeé", 5),
])
def test_search_query(provenance_dataload, client, search_query, expected_grants):
    r = client.get(f"/search?text_query={search_query}", follow=True)
    assert r.context['results']['hits']['total']['value'] == expected_grants


def test_json_download(provenance_dataload, client):
    initial_response = client.get('/search.json?text_query=gardens')
    assert initial_response.status_code == 302
    response = client.get(initial_response.url)
    json_string = b''.join(response.streaming_content).decode('utf-8')
    json.loads(json_string)


def test_orgid_with_dots(provenance_dataload, client):
    # Delf Universy request has a ".c" at the end.
    # Check that it is not seen as a format type.

    org = client.get('/org/XI-GRID-grid.5292.c')

    assert org.status_code == 200


def test_districts_datatables(provenance_dataload, client):
    datatables = client.get("/grants_datatables?draw=1&columns%5B0%5D%5Bdata%5D=title&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=amountAwarded&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=fundingOrganization.0.name&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=recipientOrganization.0.name&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=awardDate&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=description&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=desc&start=0&length=220&search%5Bvalue%5D=&search%5Bregex%5D=false&recipientDistrictName=Sir+Ddinbych+-+Denbighshire&_=1668523317785")
    assert datatables.status_code == 200


def test_region_datatables(provenance_dataload, client):
    datatbales = client.get("/grants_datatables?draw=1&columns%5B0%5D%5Bdata%5D=title&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=amountAwarded&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=fundingOrganization.0.name&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=recipientOrganization.0.name&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=awardDate&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=description&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=desc&start=0&length=220&search%5Bvalue%5D=&search%5Bregex%5D=false&recipientRegionName=Wales&_=1668523901299")
    assert datatbales.status_code == 200


def test_old_org_to_new_redirects(provenance_dataload, client):
    assert client.get("/funder/GB-CHC-1126147").status_code == 302
    assert client.get("/recipient/GB-COH-08523414").status_code == 302
    assert client.get("/publisher/GB-CHC-1126147").status_code == 302


def test_datasets_page(provenance_dataload, client):
    assert client.get("/datasets/").status_code == 200


def test_get_pagination_single_page():
    request = RequestFactory().get('/')
    context = {
        "results": {
            "hits": {
                "total": {
                    "value": 5
                }
            }
        },
        "query": BASIC_QUERY
    }
    get_pagination(request, context, 1, create_parameters_from_json_query)
    assert 1 == len(context['pages'])

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "1" == page['label']
    assert page['active']


def test_get_pagination_ten_pages_on_page_1():
    request = RequestFactory().get('/')
    context = {
        "results": {
            "hits": {
                "total": {
                    "value": 199
                }
            }
        },
        "query": BASIC_QUERY
    }
    get_pagination(request, context, 1, create_parameters_from_json_query)
    assert 6 == len(context['pages'])

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "1" == page['label']
    assert page['active']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "2" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "3" == page['label']

    page = context['pages'].pop(0)
    assert "ellipsis" == page['type']

    page = context['pages'].pop(0)
    assert "next" == page['type']

    page = context['pages'].pop(0)
    assert "last" == page['type']


def test_get_pagination_ten_pages_on_page_2():
    request = RequestFactory().get('/')
    context = {
        "results": {
            "hits": {
                "total": {
                    "value": 199
                }
            }
        },
        "query": BASIC_QUERY
    }
    get_pagination(request, context, 2, create_parameters_from_json_query)
    assert 9 == len(context['pages'])

    page = context['pages'].pop(0)
    assert "first" == page['type']

    page = context['pages'].pop(0)
    assert "prev" == page['type']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "1" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "2" == page['label']
    assert page['active']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "3" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "4" == page['label']

    page = context['pages'].pop(0)
    assert "ellipsis" == page['type']

    page = context['pages'].pop(0)
    assert "next" == page['type']

    page = context['pages'].pop(0)
    assert "last" == page['type']


def test_get_pagination_ten_pages_on_page_5():
    request = RequestFactory().get('/')
    context = {
        "results": {
            "hits": {
                "total": {
                    "value": 199
                }
            }
        },
        "query": BASIC_QUERY
    }
    get_pagination(request, context, 5, create_parameters_from_json_query)
    assert 11 == len(context['pages'])

    page = context['pages'].pop(0)
    assert "first" == page['type']

    page = context['pages'].pop(0)
    assert "prev" == page['type']

    page = context['pages'].pop(0)
    assert "ellipsis" == page['type']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "3" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "4" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "5" == page['label']
    assert page['active']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "6" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "7" == page['label']

    page = context['pages'].pop(0)
    assert "ellipsis" == page['type']

    page = context['pages'].pop(0)
    assert "next" == page['type']

    page = context['pages'].pop(0)
    assert "last" == page['type']


def test_get_pagination_ten_pages_on_page_6():
    request = RequestFactory().get('/')
    context = {
        "results": {
            "hits": {
                "total": {
                    "value": 199
                }
            }
        },
        "query": BASIC_QUERY
    }
    get_pagination(request, context, 6, create_parameters_from_json_query)
    assert 11 == len(context['pages'])

    page = context['pages'].pop(0)
    assert "first" == page['type']

    page = context['pages'].pop(0)
    assert "prev" == page['type']

    page = context['pages'].pop(0)
    assert "ellipsis" == page['type']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "4" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "5" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "6" == page['label']
    assert page['active']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "7" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "8" == page['label']

    page = context['pages'].pop(0)
    assert "ellipsis" == page['type']

    page = context['pages'].pop(0)
    assert "next" == page['type']

    page = context['pages'].pop(0)
    assert "last" == page['type']


def test_get_pagination_ten_pages_on_page_7():
    request = RequestFactory().get('/')
    context = {
        "results": {
            "hits": {
                "total": {
                    "value": 199
                }
            }
        },
        "query": BASIC_QUERY
    }
    get_pagination(request, context, 7, create_parameters_from_json_query)
    assert 11 == len(context['pages'])

    page = context['pages'].pop(0)
    assert "first" == page['type']

    page = context['pages'].pop(0)
    assert "prev" == page['type']

    page = context['pages'].pop(0)
    assert "ellipsis" == page['type']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "5" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "6" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "7" == page['label']
    assert page['active']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "8" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "9" == page['label']

    page = context['pages'].pop(0)
    assert "ellipsis" == page['type']

    page = context['pages'].pop(0)
    assert "next" == page['type']

    page = context['pages'].pop(0)
    assert "last" == page['type']


def test_get_pagination_ten_pages_on_page_8():
    request = RequestFactory().get('/')
    context = {
        "results": {
            "hits": {
                "total": {
                    "value": 199
                }
            }
        },
        "query": BASIC_QUERY
    }
    get_pagination(request, context, 8, create_parameters_from_json_query)
    assert 10 == len(context['pages'])

    page = context['pages'].pop(0)
    assert "first" == page['type']

    page = context['pages'].pop(0)
    assert "prev" == page['type']

    page = context['pages'].pop(0)
    assert "ellipsis" == page['type']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "6" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "7" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "8" == page['label']
    assert page['active']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "9" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "10" == page['label']

    page = context['pages'].pop(0)
    assert "next" == page['type']

    page = context['pages'].pop(0)
    assert "last" == page['type']


def test_get_pagination_ten_pages_on_page_9():
    request = RequestFactory().get('/')
    context = {
        "results": {
            "hits": {
                "total": {
                    "value": 199
                }
            }
        },
        "query": BASIC_QUERY
    }
    get_pagination(request, context, 9, create_parameters_from_json_query)
    assert 9 == len(context['pages'])

    page = context['pages'].pop(0)
    assert "first" == page['type']

    page = context['pages'].pop(0)
    assert "prev" == page['type']

    page = context['pages'].pop(0)
    assert "ellipsis" == page['type']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "7" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "8" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "9" == page['label']
    assert page['active']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "10" == page['label']

    page = context['pages'].pop(0)
    assert "next" == page['type']

    page = context['pages'].pop(0)
    assert "last" == page['type']


def test_get_pagination_ten_pages_on_page_10():
    request = RequestFactory().get('/')
    context = {
        "results": {
            "hits": {
                "total": {
                    "value": 199
                }
            }
        },
        "query": BASIC_QUERY
    }
    get_pagination(request, context, 10, create_parameters_from_json_query)
    assert 6 == len(context['pages'])

    page = context['pages'].pop(0)
    assert "first" == page['type']

    page = context['pages'].pop(0)
    assert "prev" == page['type']

    page = context['pages'].pop(0)
    assert "ellipsis" == page['type']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "8" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "9" == page['label']

    page = context['pages'].pop(0)
    assert "number" == page['type']
    assert "10" == page['label']
    assert page['active']


def test_pre_2020_sprint_url_compatibility(client):
    response = client.get('/search?json_query={"query"%3A+{"bool"%3A+{"must"%3A+{"query_string"%3A+{"query"%3A+"test"%2C+"default_field"%3A+"*"}}%2C+"filter"%3A+[{"bool"%3A+{"should"%3A+[]}}%2C+{"bool"%3A+{"should"%3A+[]}}%2C+{"bool"%3A+{"should"%3A+[]%2C+"must"%3A+{}%2C+"minimum_should_match"%3A+1}}%2C+{"bool"%3A+{"should"%3A+{"range"%3A+{"amountAwarded"%3A+{}}}%2C+"must"%3A+{}%2C+"minimum_should_match"%3A+1}}%2C+{"bool"%3A+{"should"%3A+[]}}%2C+{"bool"%3A+{"should"%3A+[]}}%2C+{"bool"%3A+{"should"%3A+[]}}%2C+{"bool"%3A+{"should"%3A+[]}}]}}%2C+"extra_context"%3A+{"awardYear_facet_size"%3A+3%2C+"amountAwardedFixed_facet_size"%3A+3}%2C+"sort"%3A+{"_score"%3A+{"order"%3A+"desc"}}%2C+"aggs"%3A+{"fundingOrganization"%3A+{"terms"%3A+{"field"%3A+"fundingOrganization.id_and_name"%2C+"size"%3A+3}}%2C+"recipientOrganization"%3A+{"terms"%3A+{"field"%3A+"recipientOrganization.id_and_name"%2C+"size"%3A+3}}%2C+"recipientRegionName"%3A+{"terms"%3A+{"field"%3A+"recipientRegionName"%2C+"size"%3A+3}}%2C+"recipientDistrictName"%3A+{"terms"%3A+{"field"%3A+"recipientDistrictName"%2C+"size"%3A+3}}%2C+"currency"%3A+{"terms"%3A+{"field"%3A+"currency"%2C+"size"%3A+3}}}}')
    assert response.status_code == 200
    assert response.context['text_query'] == 'test'


def test_recipientOrganization_filter_ajax(client):
    uri = reverse_lazy('filter_search_ajax')
    response = client.get(f"{uri}?parent_field=recipientOrganization&child_field=id_and_name&filter_search=a")
    assert len(json.loads(response.content)["results"]) == 100


def test_programmeTitle_filter_ajax(client):
    uri = reverse_lazy('filter_search_ajax')
    response = client.get(f"{uri}?parent_field=grantProgramme&child_field=title_keyword&filter_search=a")
    assert len(json.loads(response.content)["results"]) == 23


def test_district_filter_ajax(client):
    uri = reverse_lazy('filter_search_ajax')
    response = client.get(f"{uri}?parent_field=additional_data&child_field=recipientDistrictName&filter_search=a")
    assert len(json.loads(response.content)["results"]) == 73
