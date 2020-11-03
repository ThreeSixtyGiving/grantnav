import json
import time

import pytest
import requests

from dataload.import_to_elasticsearch import import_to_elasticsearch, get_area_mappings

prefix = 'https://raw.githubusercontent.com/OpenDataServices/grantnav-sampledata/b6135e6fb8960323031e9013bf55b5391fd243a9/'


@pytest.fixture(scope="module")
def dataload():
    get_area_mappings()
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


def test_help_page(provenance_dataload, client):
    response = client.get('/help')
    assert 'Help with using GrantNav' in str(response.content)


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
