import json
import time

import pytest
import requests

from dataload.import_to_elasticsearch import import_to_elasticsearch
from grantnav.frontend.views import get_pagination, BASIC_QUERY
from django.test.client import RequestFactory
from django.urls import reverse_lazy


prefix = 'https://raw.githubusercontent.com/OpenDataServices/grantnav-sampledata/44ea7fdad8f32e9fab1d870e2f25fc31c5cdf2fd/'


@pytest.fixture(scope="module")
def dataload():
    import_to_elasticsearch(
        [
            prefix + 'a002400000KeYdsAAF.json',
            prefix + 'grantnav-20180903134856.json',
            prefix + 'a002400000nO46WAAS.json'
        ], clean=True
    )
    #elastic search needs some time to commit its data
    time.sleep(2)


@pytest.fixture(scope="function")
def provenance_dataload(dataload, settings, tmpdir):
    local_data_json = tmpdir.join('data.json')
    local_data_json.write(requests.get(prefix + 'data.json').content)
    settings.PROVENANCE_JSON = local_data_json.strpath


@pytest.mark.parametrize(('expected_text'), [
    ('GrantNav'),
    ('Search'),
    ('Help'),
    ])
def test_home(provenance_dataload, client, expected_text):
    response = client.get('/')
    assert expected_text in str(response.content)
    assert "grant-making" not in str(response.content)


def test_search(provenance_dataload, client):
    initial_response = client.get('/search?text_query=gardens+AND+fundingOrganization.id:GB-CHC-1156077')
    assert initial_response.status_code == 302
    response = client.get(initial_response.url)
    assert "Total grants" in str(response.content)
    assert "The British Museum" in str(response.content)

    assert response.context['text_query'] == 'gardens AND fundingOrganization.id:GB-CHC-1156077'
    assert response.context['results']['hits']['total']['value'] == 7

    # click facet
    wolfson_facet = response.context['results']['aggregations']['fundingOrganization']['buckets'][0]
    assert wolfson_facet['doc_count'] == 7
    assert wolfson_facet['key'] == '["Wolfson Foundation", "GB-CHC-1156077"]'

    # click again
    response = client.get(wolfson_facet['url'])
    wolfson_facet = response.context['results']['aggregations']['fundingOrganization']['buckets'][0]
    assert wolfson_facet['doc_count'] == 7
    assert wolfson_facet['key'] == '["Wolfson Foundation", "GB-CHC-1156077"]'

    # Test the data is extended by grantnav adding geo codes
    # Original data contains postal codes only
    geocode_response = client.get('/search?text_query=E10000023+AND+fundingOrganization.id:GB-CHC-1156077')
    response = client.get(geocode_response.url)
    assert response.context['results']['hits']['total']['value'] == 0

    geocode_response = client.get('/search?text_query=E09000033+AND+fundingOrganization.id:GB-CHC-1156077')
    response = client.get(geocode_response.url)
    assert response.context['results']['hits']['total']['value'] == 19


def test_search_accents(provenance_dataload, client):
    # Check that accents placed in different positions give same result

    initial_response = client.get('/search?text_query=Esmee')
    response = client.get(initial_response.url)

    assert response.context['results']['hits']['total']['value'] == 5

    initial_response = client.get('/search?text_query=Esmée')
    response = client.get(initial_response.url)

    assert response.context['results']['hits']['total']['value'] == 5

    initial_response = client.get('/search?text_query=Esmeé')
    response = client.get(initial_response.url)

    assert response.context['results']['hits']['total']['value'] == 5


#def test_stats(provenance_dataload, client):
#    response = client.get('/stats')
#    assert "379" in str(response.content)


def test_json_download(provenance_dataload, client):
    initial_response = client.get('/search.json?text_query=gardens')
    assert initial_response.status_code == 302
    response = client.get(initial_response.url)
    json_string = b''.join(response.streaming_content).decode('utf-8')
    json.loads(json_string)


def test_orgid_with_dots(provenance_dataload, client):
    # Delf Universy request has a ".c" at the end.
    # Check that it is not seen as a format type.

    recipient = client.get('/recipient/XI-GRID-grid.5292.c')

    assert recipient.status_code == 200


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
    get_pagination(request, context, 1)
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
    get_pagination(request, context, 1)
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
    get_pagination(request, context, 2)
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
    get_pagination(request, context, 5)
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
    get_pagination(request, context, 6)
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
    get_pagination(request, context, 7)
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
    get_pagination(request, context, 8)
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
    get_pagination(request, context, 9)
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
    get_pagination(request, context, 10)
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
