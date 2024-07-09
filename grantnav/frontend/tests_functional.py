import os
import time
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common import exceptions as selenium_exceptions
import chromedriver_autoinstaller

from dataload.import_to_elasticsearch import import_to_elasticsearch

# Test data directory
prefix = f"{os.path.dirname(__file__)}/../../dataload/test_data/"

chromedriver_autoinstaller.install()
BROWSER = os.environ.get('BROWSER', 'ChromeHeadless')


def check_js_errors(browser):
    for log in browser.get_log("browser"):
        assert "SEVERE" not in log['level'], f"found {log}"


@pytest.fixture(scope="module")
def browser(request):
    if BROWSER == 'ChromeHeadless':
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        # no-sandbox prevents an error when running as the root user
        chrome_options.add_argument("--no-sandbox")
        # uncomment this if "DevToolsActivePort" error / ubuntu snap workaround
        chrome_options.add_argument("--remote-debugging-port=9222")
        # chrome_options.add_argument('ignore-unexpected-deprecations')
        browser = webdriver.Chrome(options=chrome_options)
    elif BROWSER == "Firefox":
        # Make downloads work
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", os.getcwd())
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/json")
        browser = getattr(webdriver, BROWSER)(firefox_profile=profile)
    else:
        browser = getattr(webdriver, BROWSER)()
    browser.implicitly_wait(3)
    request.addfinalizer(lambda: browser.quit())
    return browser


@pytest.fixture(scope="module")
def server_url(request, live_server):
    if "CUSTOM_SERVER_URL" in os.environ:
        return os.environ["CUSTOM_SERVER_URL"]
    else:
        return live_server.url


@pytest.fixture(scope="module")
def dataload():
    import_to_elasticsearch(
        [
            prefix + "a002400000KeYdsAAF-currency.json",
            prefix + "a002400000OiDBQAA3.json",
            prefix + "awefw001p00000zgyHZAAY.json",
        ],
        clean=True,
        funders=os.path.join(prefix, "funders.jl"),
        recipients=os.path.join(prefix, "recipients.jl"),
    )
    # elastic search needs some time to commit its data
    time.sleep(2)


@pytest.fixture(scope="function")  # FIXME autouse=True
def provenance_dataload(dataload, settings, tmpdir):
    settings.PROVENANCE_JSON = os.path.join(prefix, "data.json")


def test_home(provenance_dataload, server_url, browser):
    browser.get(server_url)
    assert 'GrantNav' in browser.find_element_by_tag_name('body').text

    # Cookie banner is currently disabled until analytics issues are resolved
    # assert 'Cookies disclaimer' in browser.find_element_by_id('CookielawBanner').text
    # browser.find_element_by_class_name("btn").click()
    browser.get(server_url)
    # assert 'Cookies disclaimer' not in browser.find_element_by_tag_name('body').text
    assert '360Giving Data Standard' in browser.find_element_by_tag_name('body').text
    assert '360Giving data standard' not in browser.find_element_by_tag_name('body').text
    check_js_errors(browser)


@pytest.mark.parametrize(('link_text'), [
    ('About the data'),
    ('Get Help'),
    ])
def test_navbar_links(provenance_dataload, server_url, browser, link_text):
    browser.get(server_url)
    browser.find_element_by_link_text(link_text)


@pytest.mark.parametrize(('link_text'), [
    ('About'),
    ('Funders'),
    ('Recipients'),
    ('Data sources used in GrantNav'),
    ('Reusing GrantNav Data'),
    ('Developers')
    ])
def test_footer_links(provenance_dataload, server_url, browser, link_text):
    browser.get(server_url)
    browser.find_element_by_link_text(link_text)


def test_search(provenance_dataload, server_url, browser):
    browser.get(server_url)
    browser.find_element_by_class_name("large-search-button").click()
    # Total number of expected grants
    assert "4,649" in \
        browser.find_element_by_class_name('search-summary-description').text

    # open show highlighted grants section
    browser.find_element_by_class_name("summary-icon").click()

    # other_currencies_modal = browser.find_element_by_id("other-currencies-modal")
    # search "laboratory"
    other_currencies_modal = browser.find_element_by_xpath("//a[@id='other-currencies-modal']/span")
    assert other_currencies_modal.text == '4'
    other_currencies_modal.click()
    time.sleep(0.5)

    # browser.get_screenshot_as_file("screenshot-test_search.png")
    assert "$153,934" in browser.find_element_by_id('summary-info-model').text
    check_js_errors(browser)


def test_search_by_titles_and_descriptions_radio_button_in_search(provenance_dataload, server_url, browser):
    browser.get(server_url)
    browser.find_element_by_class_name("large-search-button").click()

    assert "Titles & Descriptions" in browser.find_element_by_tag_name('body').text


def test_search_by_titles_and_descriptions(provenance_dataload, server_url, browser):
    browser.get(server_url)
    # search "laboratory"
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('laboratory')
    browser.find_element_by_class_name("large-search-button").click()
    try:
        browser.find_element_by_class_name("cookie-consent-no").click()
    except selenium_exceptions.NoSuchElementException:
        pass
    # select title_and_description
    browser.find_element_by_xpath("//label[@for='title_and_description']").click()
    browser.find_element_by_class_name("large-search-button").click()

    assert "New science laboratory" in browser.find_element_by_tag_name('body').text
    assert "laboratories" in browser.find_element_by_tag_name('body').text

    assert "Your search ‘laboratory’ returned 22 results in ‘Titles & Descriptions’" \
        in browser.find_element_by_class_name('search-summary-description').text

    browser.get(server_url)
    # search "laboratory" in "Search All"
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('laboratory')
    browser.find_element_by_class_name("large-search-button").click()

    assert "New science laboratory" in browser.find_element_by_tag_name('body').text
    assert "laboratories" in browser.find_element_by_tag_name('body').text

    assert "Your search ‘laboratory’ returned 23 results in ‘All grant fields’" \
        in browser.find_element_by_class_name('search-summary-description').text


def test_search_current_url(provenance_dataload, server_url, browser):
    browser.get(server_url)
    browser.find_element_by_class_name("large-search-button").click()

    current_url_split_by_json_query = browser.current_url.split('?')
    assert current_url_split_by_json_query[0][-6:] == 'search'


# def test_search_two_words_without_quotes(provenance_dataload, server_url, browser):
#     """
#     When a user's search query is 2+ words without quotes,
#     we want to inform the user that with quotes will have a better search result.
#     """
#     browser.get(server_url)
#     search_box = browser.find_element_by_class_name("large-search")
#     search_box.send_keys('social change')
#     browser.find_element_by_class_name("large-search-button").click()

#     assert 'If you\'re looking for a specific phrase, put quotes around it to refine your search. e.g. "youth clubs".' \
#            in browser.find_element_by_tag_name('body').text


def test_search_two_words_with_single_quotes(provenance_dataload, server_url, browser):
    browser.get(server_url)
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys("'social change'")
    browser.find_element_by_class_name("large-search-button").click()

    assert 'If you\'re looking for a specific phrase, put quotes around it to refine your search. e.g. "youth clubs".' \
           not in browser.find_element_by_tag_name('body').text


def test_search_two_words_with_double_quotes(provenance_dataload, server_url, browser):
    browser.get(server_url)
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('"social change"')
    browser.find_element_by_class_name("large-search-button").click()

    assert 'If you\'re looking for a specific phrase, put quotes around it to refine your search. e.g. "youth clubs".' \
           not in browser.find_element_by_tag_name('body').text


def test_search_two_words_with_hyphen(provenance_dataload, server_url, browser):
    """
    When a user's search query is 2 words with a hyphen,
    we want to inform the user that with quotes will have a better search result.
    """
    browser.get(server_url)
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('covid-19')
    browser.find_element_by_class_name("large-search-button").click()

    assert 'If you\'re looking for a specific phrase, put quotes around it to refine your search. e.g. "youth clubs".' \
           in browser.find_element_by_tag_name('body').text


def test_search_includes_and(provenance_dataload, server_url, browser):
    """
    When a user's search query includes 'and', we want to inform the user of what it means.
    """
    browser.get(server_url)
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('mental and health')
    browser.find_element_by_class_name("large-search-button").click()

    assert 'The AND keyword (not case-sensitive) means that results must have both words present. ' \
           'If you\'re looking for a phrase that has the word "and" in it, put quotes around the phrase ' \
           '(e.g. "fees and costs").' in browser.find_element_by_tag_name('body').text


def test_search_does_not_include_and(provenance_dataload, server_url, browser):
    browser.get(server_url)
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('secondhand clothes')
    browser.find_element_by_class_name("large-search-button").click()

    assert 'The AND keyword (not case-sensitive) means that results must have both words present. ' \
           'If you\'re looking for a phrase that has the word "and" in it, put quotes around the phrase ' \
           '(e.g. "fees and costs").' not in browser.find_element_by_tag_name('body').text


def test_search_includes_or(provenance_dataload, server_url, browser):
    """
    When a user's search query includes 'or', we want to inform the user of what it means.
    """
    browser.get(server_url)
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('mental or health')
    browser.find_element_by_class_name("large-search-button").click()

    assert 'The OR keyword (not case-sensitive) means that results must have one of the words present. ' \
           'This is the default. If you\'re looking for a phrase that has the word "or" in ' \
           '(e.g. "children or adults"), put quotes around it.' in browser.find_element_by_tag_name('body').text


def test_search_does_not_include_or(provenance_dataload, server_url, browser):
    browser.get(server_url)
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('meteor clothes')
    browser.find_element_by_class_name("large-search-button").click()

    assert 'The OR keyword (not case-sensitive) means that results must have one of the words present. ' \
           'This is the default. If you\'re looking for a phrase that has the word "or" in ' \
           '(e.g. "children or adults"), put quotes around it.' not in browser.find_element_by_tag_name('body').text


def test_search_display_tip(provenance_dataload, server_url, browser):
    """
    When an advance search message is displayed in the search results,
    'Tip: ' will appear in front of the message.
    """
    browser.get(server_url)
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('social change')
    browser.find_element_by_class_name("large-search-button").click()

    assert 'Tip: ' in browser.find_element_by_tag_name('body').text


def test_search_do_not_display_tip(provenance_dataload, server_url, browser):
    browser.get(server_url)
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('grant')
    browser.find_element_by_class_name("large-search-button").click()

    assert 'Tip: ' not in browser.find_element_by_tag_name('body').text


def test_search_display_advanced_search_link(provenance_dataload, server_url, browser):
    """
    When an advance search message is displayed in the search results,
    a link to the 'advance search' information page is also included.
    """
    browser.get(server_url)
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('social change')
    browser.find_element_by_class_name("large-search-button").click()

    assert 'For more tips, see Advanced Search' in browser.find_element_by_tag_name('body').text


def test_search_advanced_search_correct_link(provenance_dataload, server_url, browser):
    browser.get(server_url)
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('social change')
    browser.find_element_by_class_name("large-search-button").click()

    try:
        browser.find_element_by_class_name("cookie-consent-no").click()
    except selenium_exceptions.NoSuchElementException:
        pass

    browser.find_element_by_link_text("targeting your search").click()


def test_search_do_not_display_advance_search_link(provenance_dataload, server_url, browser):
    browser.get(server_url)
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('grant')
    browser.find_element_by_class_name("large-search-button").click()

    assert 'For more tips, see Advanced Search' not in browser.find_element_by_tag_name('body').text


def test_bad_search(provenance_dataload, server_url, browser):
    browser.get(server_url)
    browser.find_element_by_name("text_query").send_keys(" £s:::::afdsfas")
    browser.find_element_by_class_name("large-search-button").click()
    not_valid = browser.find_element_by_id('not_valid').text
    assert 'Search input is not valid' in not_valid
    assert "We can't find what you tried to search for." in not_valid


def test_terms(server_url, browser):
    browser.get(server_url + '/terms')
    assert 'Terms and conditions' in browser.find_element_by_tag_name('h1').text


def test_title(server_url, browser):
    browser.get(server_url)
    assert '360Giving GrantNav' in browser.title


def test_no_results_page(server_url, browser):
    browser.get(server_url)
    search_box = browser.find_element_by_class_name("large-search")
    search_box.send_keys('dfsergegrdtytdrthgrtyh')
    browser.find_element_by_class_name("large-search-button").click()

    no_results = browser.find_element_by_id('no-results').text
    assert 'No Results' in no_results
    assert 'Your search - "dfsergegrdtytdrthgrtyh" - did not match any grant records.' in no_results


def test_datasets_page(server_url, browser):
    browser.get(server_url + '/datasets')
    assert 'Data used in GrantNav' in browser.find_element_by_tag_name('h1').text
    check_js_errors(browser)


@pytest.mark.parametrize(('path', 'text'), [
    ('/grant/360G-LBFEW-111657', 'Where is this data from?'),
    ('/grant/360G-LBFEW-111657', 'This data was originally published by')
    ])
def test_disclaimers(server_url, browser, path, text):
    browser.get(server_url + path)
    assert text in browser.find_element_by_tag_name('body').text
    check_js_errors(browser)


def test_currency_facet(provenance_dataload, server_url, browser):
    browser.get(server_url)
    browser.find_element_by_class_name("large-search-button").click()

    try:
        browser.find_element_by_class_name("cookie-consent-no").click()
    except selenium_exceptions.NoSuchElementException:
        pass

    # Select USD
    # browser.get_screenshot_as_file("test2.png")
    # Open the filter group expander
    browser.find_element_by_id("filter-accordion-currency").click()
    browser.find_element_by_id("filter-option-currency-usd").click()

    # Check USD options appear
    assert 'USD 0 - USD 500' in browser.find_element_by_tag_name('body').text


def test_amount_awarded_facet(provenance_dataload, server_url, browser):
    browser.get(server_url)
    browser.find_element_by_class_name("large-search-button").click()

    try:
        browser.find_element_by_class_name("cookie-consent-no").click()
    except selenium_exceptions.NoSuchElementException:
        pass

    #  browser.get_screenshot_as_file("test3.png")
    # Select an amount option
    browser.find_element_by_id("amount-1000.0-5000.0").click()
    total_grants = browser.find_elements_by_css_selector(".summary-content--item span")[0].text
    assert "49" in total_grants, "Expected number of grants not found"


@pytest.mark.parametrize(('path'), ['/grant/360G-LBFEW-99233'])
def test_zero_grant_info_link_absent(provenance_dataload, server_url, browser, path):
    browser.get(server_url + path)
    assert len(browser.find_elements_by_id('zero_value_grant_help_link')) == 0


def test_search_recipients(provenance_dataload, server_url, browser):
    browser.get(server_url + "/recipients")

    try:
        browser.find_element_by_class_name("cookie-consent-no").click()
    except selenium_exceptions.NoSuchElementException:
        pass

    browser.find_element_by_name("text_query").send_keys("Social Justice")
    browser.find_element_by_class_name("large-search-button").click()

    #browser.get_screenshot_as_file("recipients-search.png")

    assert len(browser.find_elements_by_class_name("grant-search-result__recipients")) == 20
    check_js_errors(browser)


def test_search_funders(provenance_dataload, server_url, browser):
    browser.get(server_url + "/funders")

    try:
        browser.find_element_by_class_name("cookie-consent-no").click()
    except selenium_exceptions.NoSuchElementException:
        pass

    browser.find_element_by_name("text_query").send_keys("foundation")
    browser.find_element_by_class_name("large-search-button").click()

    #browser.get_screenshot_as_file("recipients-search.png")

    assert len(browser.find_elements_by_class_name("grant-search-result__funders")) == 20
    check_js_errors(browser)


def test_org_page(provenance_dataload, server_url, browser):
    browser.get(server_url + "/org/GB-CHC-1156077")
    #browser.get_screenshot_as_file("org-page.png")

    assert "Wolfson Foundation" in browser.find_element_by_tag_name('h1').text
    check_js_errors(browser)


def test_insights_button(provenance_dataload, server_url, browser):
    """ Tests that the insights button takes us to an Insights site """

    for button in browser.find_elements_by_css_selector("a[data='insights-integration-btn']"):
        # Narrow search results to fewer than 10k
        browser.get(server_url + "/search?currency=AUD")
        button.click()
        assert browser.find_element_by_tag_name("title").text == "360Insights"
        # Clear browser log for external site
        browser.get_log("browser")


links_checked = {}


@pytest.mark.parametrize(('path'), ['?',
                                    '/search',
                                    '/funders',
                                    '/recipients',
                                    '/about',
                                    '/datasets',
                                    '/grant/360G-LBFEW-99233',  # regular grant
                                    '/grant/360G-wolfson-19916y',  # grant with 0 or negative amount
                                    '/org/GB-CHC-1126147'])
def test_links(provenance_dataload, server_url, browser, path):
    """ Load each path and check the links within the page respond HTTP success """

    # We use selenium for this kind of test because it's a convenient way to manipulate the dom
    browser.get(server_url + path)
    skip = ["#", "https://twitter.com/360Giving/", "mailto:grantnav@threesixtygiving.org", "https://insights.threesixtygiving.org/?url=https://grantnav.threesixtygiving.org/search.json%3F"]

    for a in browser.find_elements_by_tag_name("a"):
        # Datatables quirk with empty <a> tags, select2 quirk with same issue
        if a.get_attribute("aria-controls") or a.get_attribute("class") == "remove-select2-option":
            continue

        link = a.get_attribute("href")

        assert link is not None, f"Error An <a> tag without a href attribute on {path} {a.get_attribute('outerHTML')}"

        if link in skip:
            continue

        # print(f"Testing {link}")

        try:
            status_code = links_checked[link]
        except KeyError:
            try:
                # Some sites reject connection without a user agent
                r = requests.head(link, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"})
            except Exception as e:
                # Convert exception to assert for better readability
                assert False, f"Request exception: {e} on {a.get_attribute('outerHTML')}"

            status_code = r.status_code
            links_checked[link] = r.status_code

            assert (status_code >= 200 and status_code < 399), f"{link} is broken: {status_code} on page {path}"
