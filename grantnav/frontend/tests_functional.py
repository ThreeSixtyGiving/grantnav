import os
import glob
import time
import pytest
from dataload.import_to_elasticsearch import import_to_elasticsearch
from selenium import webdriver

prefix = 'https://raw.githubusercontent.com/OpenDataServices/grantnav-sampledata/c555725bf1aa1e2d22fb69dd99c1831feff7ecbd/'


BROWSER = os.environ.get('BROWSER', 'Firefox')


@pytest.fixture(scope="module")
def browser(request):
    if BROWSER == "Firefox":
        # Make downloads work
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", os.getcwd())
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/json")
        browser = getattr(webdriver, BROWSER)(firefox_profile=profile)
        browser.implicitly_wait(3)
        request.addfinalizer(lambda: browser.quit())
        return browser
    else:
        browser = getattr(webdriver, BROWSER)()
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
    import_to_elasticsearch([prefix + 'wolfson.json',
                             prefix + '360_giving_LBFEW_2010_2015.xlsx',
                             prefix + 'IndigoTrust_360giving.csv'], clean=True)
    #elastic search needs some time to commit its data
    time.sleep(2)


def test_home(dataload, server_url, browser):
    browser.get(server_url)
    assert 'GrantNav' in browser.find_element_by_tag_name('body').text
    browser.find_element_by_link_text("Terms and Conditions")
    browser.find_element_by_link_text("Take Down Policy")

    assert 'Cookies disclaimer' in browser.find_element_by_id('CookielawBanner').text
    browser.find_element_by_class_name("btn").click()
    browser.get(server_url)
    assert 'Cookies disclaimer' not in browser.find_element_by_tag_name('body').text


@pytest.mark.parametrize(('text'), [
    ('Contains OS data © Crown copyright and database right 2016'),
    ('Contains Royal Mail data © Royal Mail copyright and Database right 2016'),
    ('Contains National Statistics data © Crown copyright and database right 2016')
    ])
def test_code_point_credit(dataload, server_url, browser, text):
    browser.get(server_url)
    code_point_paragraph = browser.find_element_by_id("code-point").text
    assert text in code_point_paragraph


def test_search(dataload, server_url, browser):
    browser.get(server_url)
    browser.find_element_by_class_name("large-search-icon").click()
    assert 'Total: 4,764' in browser.find_element_by_tag_name('body').text
    assert 'Lloyds Bank Foundation for England and Wales (4,116)' in browser.find_element_by_tag_name('body').text
    assert 'Wolfson Foundation (379)' in browser.find_element_by_tag_name('body').text


def test_bad_search(dataload, server_url, browser):
    browser.get(server_url)
    browser.find_element_by_name("text_query").send_keys(" £s:::::afdsfas")
    browser.find_element_by_class_name("large-search-icon").click()
    assert 'Search input is not valid' in browser.find_element_by_tag_name('body').text


def test_terms(server_url, browser):
    browser.get(server_url + '/terms')
    assert 'Terms & conditions' in browser.find_element_by_tag_name('h1').text


def test_take_down(server_url, browser):
    browser.get(server_url + '/take_down_policy')
    assert 'Take Down Policy' in browser.find_element_by_tag_name('h1').text
