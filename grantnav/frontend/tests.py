import json
import time
import urllib.parse

import pytest
import requests

from dataload.import_to_elasticsearch import import_to_elasticsearch, get_area_mappings

prefix = 'https://raw.githubusercontent.com/OpenDataServices/grantnav-sampledata/560a8d9f21a069a9d51468850188f34ae72a0ec3/'


@pytest.fixture(scope="module")
def dataload():
    get_area_mappings()
    import_to_elasticsearch([prefix + 'a002400000KeYdsAAF.json'], clean=True)
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
    initial_response = client.get('/search?text_query=gardens')
    assert initial_response.status_code == 302
    response = client.get(initial_response.url)
    assert "Total grants" in str(response.content)
    assert "The British Museum" in str(response.content)

    assert response.context['text_query'] == 'gardens'
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
    geocode_response = client.get('/search?text_query=E10000023')
    response = client.get(geocode_response.url)
    assert response.context['results']['hits']['total'] == 0

    geocode_response = client.get('/search?text_query=E09000033')
    response = client.get(geocode_response.url)
    assert response.context['results']['hits']['total'] == 19


def test_esmee_gives_results(provenance_dataload, client):
    initial_response = client.get('/search?text_query=Esmee')
    response = client.get(initial_response.url)

    assert 'Esm' in str(response.content)
    assert 'Esme' in str(response.content)
    assert 'Esmee' in str(response.content)


def test_esmée_gives_results(provenance_dataload, client):
    initial_response = client.get('/search?text_query=Esmée')
    response = client.get(initial_response.url)

    assert 'Esm' in str(response.content)
    assert 'Esme' in str(response.content)
    assert 'Esmee' in str(response.content)


def test_esmeé_gives_results(provenance_dataload, client):
    initial_response = client.get('/search?text_query=Esmeé')
    response = client.get(initial_response.url)
    print(response.content)
    assert 'Esm' in str(response.content)
    assert 'Esme' in str(response.content)
    assert 'Esmee' in str(response.content)


# one = http://grantnav.threesixtygiving.org/search?json_query=%7B%22extra_context%22%3A+%7B%22awardYear_facet_size%22%3A+3%2C+%22amountAwardedFixed_facet_size%22%3A+3%7D%2C+%22aggs%22%3A+%7B%22recipientDistrictName%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22recipientDistrictName%22%7D%7D%2C+%22recipientOrganization%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22recipientOrganization.id_and_name%22%7D%7D%2C+%22recipientRegionName%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22recipientRegionName%22%7D%7D%2C+%22fundingOrganization%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22fundingOrganization.id_and_name%22%7D%7D%2C+%22currency%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22currency%22%7D%7D%7D%2C+%22query%22%3A+%7B%22bool%22%3A+%7B%22must%22%3A+%7B%22query_string%22%3A+%7B%22default_field%22%3A+%22_all%22%2C+%22
# query%22%3A+%22Esmee%22%7D%7D%2C+%22
# filter%22%3A+%5B%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22must%22%3A+%7B%7D%2C+%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22must%22%3A+%7B%7D%2C+%22should%22%3A+%7B%22range%22%3A+%7B%22amountAwarded%22%3A+%7B%7D%7D%7D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%5D%7D%7D%2C+%22sort%22%3A+%7B%22_score%22%3A+%7B%22order%22%3A+%22desc%22%7D%7D%7D
#
# two = http://grantnav.threesixtygiving.org/search?json_query=%7B%22extra_context%22%3A+%7B%22awardYear_facet_size%22%3A+3%2C+%22amountAwardedFixed_facet_size%22%3A+3%7D%2C+%22aggs%22%3A+%7B%22recipientDistrictName%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22recipientDistrictName%22%7D%7D%2C+%22recipientOrganization%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22recipientOrganization.id_and_name%22%7D%7D%2C+%22recipientRegionName%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22recipientRegionName%22%7D%7D%2C+%22fundingOrganization%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22fundingOrganization.id_and_name%22%7D%7D%2C+%22currency%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22currency%22%7D%7D%7D%2C+%22query%22%3A+%7B%22bool%22%3A+%7B%22must%22%3A+%7B%22query_string%22%3A+%7B%22default_field%22%3A+%22_all%22%2C+%22
# query%22%3A+%22Esm%5Cu00e9e%22%7D%7D%2C+%22
# query%22%3A+%22Esm%5Cu00e9e%22%2C+%22
# filter%22%3A+%5B%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22must%22%3A+%7B%7D%2C+%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22must%22%3A+%7B%7D%2C+%22should%22%3A+%7B%22range%22%3A+%7B%22amountAwarded%22%3A+%7B%7D%7D%7D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%5D%7D%7D%2C+%22sort%22%3A+%7B%22_score%22%3A+%7B%22order%22%3A+%22desc%22%7D%7D%7D
#
# thr = http://grantnav.threesixtygiving.org/search?json_query=%7B%22extra_context%22%3A+%7B%22awardYear_facet_size%22%3A+3%2C+%22amountAwardedFixed_facet_size%22%3A+3%7D%2C+%22aggs%22%3A+%7B%22recipientDistrictName%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22recipientDistrictName%22%7D%7D%2C+%22recipientOrganization%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22recipientOrganization.id_and_name%22%7D%7D%2C+%22recipientRegionName%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22recipientRegionName%22%7D%7D%2C+%22fundingOrganization%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22fundingOrganization.id_and_name%22%7D%7D%2C+%22currency%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22currency%22%7D%7D%7D%2C+%22query%22%3A+%7B%22bool%22%3A+%7B%22must%22%3A+%7B%22query_string%22%3A+%7B%22default_field%22%3A+%22_all%22%2C+%22
# query%22%3A+%22Esme%5Cu00e9%22%7D%7D%2C+%22
# query%22%3A+%22Esme%5Cu00e9%22%2C+%22
# filter%22%3A+%5B%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22must%22%3A+%7B%7D%2C+%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22must%22%3A+%7B%7D%2C+%22should%22%3A+%7B%22range%22%3A+%7B%22amountAwarded%22%3A+%7B%7D%7D%7D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%5D%7D%7D%2C+%22sort%22%3A+%7B%22_score%22%3A+%7B%22order%22%3A+%22desc%22%7D%7D%7D



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
