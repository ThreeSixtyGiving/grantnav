import json
import time
import urllib.parse

import pytest
import requests

from dataload.import_to_elasticsearch import import_to_elasticsearch, get_area_mappings

prefix = 'https://raw.githubusercontent.com/OpenDataServices/grantnav-sampledata/c536a0ee750893fb53e7b458248fd8fd5913e9b5/'


@pytest.fixture(scope="module")
def dataload():
    get_area_mappings()
    import_to_elasticsearch([prefix + 'a002400000KeYdsAAF.json', prefix + 'grantnav-20180903134856.json'], clean=True)
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
    ('Advanced Search')
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
    assert response.context['results']['hits']['total'] == 8

    # click facet
    wolfson_facet = response.context['results']['aggregations']['fundingOrganization']['buckets'][0]
    assert wolfson_facet['doc_count'] == 8
    assert wolfson_facet['key'] == '["Wolfson Foundation", "GB-CHC-1156077"]'
    json_query = json.loads(urllib.parse.parse_qs(initial_response.url.split('?')[-1])['json_query'][0])

    json_query['query']['bool']['filter'][0]['bool']['should'] = [{'term': {'fundingOrganization.id_and_name': '["Wolfson Foundation", "GB-CHC-1156077"]'}}]
    assert json.loads(urllib.parse.parse_qs(wolfson_facet['url'].split('?')[-1])['json_query'][0]) == json_query

    # click again
    response = client.get(wolfson_facet['url'])
    wolfson_facet = response.context['results']['aggregations']['fundingOrganization']['buckets'][0]
    assert wolfson_facet['doc_count'] == 8
    assert wolfson_facet['key'] == '["Wolfson Foundation", "GB-CHC-1156077"]'
    json_query['query']['bool']['filter'][0]['bool']['should'] = []
    assert json.loads(urllib.parse.parse_qs(wolfson_facet['url'].split('?')[-1])['json_query'][0]) == json_query

    # Test the data is extended by grantnav adding geo codes
    # Original data contains postal codes only
    geocode_response = client.get('/search?text_query=E10000023+AND+fundingOrganization.id:GB-CHC-1156077')
    response = client.get(geocode_response.url)
    assert response.context['results']['hits']['total'] == 0

    geocode_response = client.get('/search?text_query=E09000033+AND+fundingOrganization.id:GB-CHC-1156077')
    response = client.get(geocode_response.url)
    assert response.context['results']['hits']['total'] == 19


def test_search_accents(provenance_dataload, client):
    # Check that accents placed in different positions give same result

    initial_response = client.get('/search?text_query=Esmee')
    response = client.get(initial_response.url)

    assert response.context['results']['hits']['total'] == 5

    initial_response = client.get('/search?text_query=Esmée')
    response = client.get(initial_response.url)

    assert response.context['results']['hits']['total'] == 5

    initial_response = client.get('/search?text_query=Esmeé')
    response = client.get(initial_response.url)

    assert response.context['results']['hits']['total'] == 5


def test_stats(provenance_dataload, client):
    response = client.get('/stats')
    assert "379" in str(response.content)


def test_help_page(provenance_dataload, client):
    response = client.get('/help')
    assert 'Using GrantNav' in str(response.content)


def test_json_download(provenance_dataload, client):
    initial_response = client.get('/search.json?text_query=gardens')
    assert initial_response.status_code == 302
    response = client.get(initial_response.url)
    json_string = b''.join(response.streaming_content).decode('utf-8')
    json.loads(json_string)
