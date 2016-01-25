import os
import time
import pytest
from dataload.import_to_elasticsearch import import_to_elasticsearch 
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

@pytest.fixture(scope="module")
def browser(request):
    browser = webdriver.Firefox()
    browser.implicitly_wait(3)
    request.addfinalizer(lambda: browser.quit())
    return browser

@pytest.fixture(scope="module")
def server_url(request, live_server):
    if 'CUSTOM_SERVER_URL' in os.environ:
        return os.environ['CUSTOM_SERVER_URL']
    else:
        return live_server.url

@pytest.fixture(scope="module")
def dataload():
    import_to_elasticsearch(['sample_data/wolfson.json',
                             'sample_data/360_giving_LBFEW_2010_2015.xlsx',
                             'sample_data/IndigoTrust_360giving.csv'], clean=True)
    #elastic search needs some time to commit its data
    time.sleep(2)


def test_home(dataload, server_url, browser):
    browser.get(server_url)
    assert 'GrantNav' in browser.find_element_by_tag_name('body').text

def test_search(dataload, server_url, browser):
    browser.get(server_url)
    browser.find_element_by_xpath("//button[contains(.,'Search')]").click()
    assert 'Total: 4764' in browser.find_element_by_tag_name('body').text
    assert 'Lloyds Bank Foundation for England and Wales (4116)' in browser.find_element_by_tag_name('body').text
    assert 'Wolfson Foundation (379)' in browser.find_element_by_tag_name('body').text


