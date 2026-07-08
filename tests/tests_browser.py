import os
import time
from urllib.parse import urlparse

from django.test import override_settings
from django.urls import reverse_lazy

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import chromedriver_autoinstaller

from tests.browser_test_case import BrowserTestCase

# Test data directory
prefix = os.path.join(os.path.dirname(__file__), "data")

chromedriver_autoinstaller.install()


@override_settings(
    PROVENANCE_JSON=os.path.join(prefix, "data.json"), DISABLE_COOKIE_POPUP=True
)
class InteractionsTests(BrowserTestCase):
    def wait_for_results_page(self):
        # Wait for the various redirects and rendering after click
        time.sleep(0.5)
        for i in range(0, 120):
            if "sort" not in self.browser.current_url:
                time.sleep(0.5)

    def test_home(self):
        server_url = reverse_lazy("home")
        self.get(server_url)
        assert "GrantNav" in self.browser.find_element(By.TAG_NAME, "body").text

        # Cookie banner is currently disabled until analytics issues are resolved
        # assert 'Cookies disclaimer' in browser.find_element(By.ID, 'CookielawBanner').text
        # browser.find_element(By.CLASS_NAME, "btn").click()
        self.get(server_url)
        # assert 'Cookies disclaimer' not in browser.find_element(By.TAG_NAME, 'body').text
        assert (
            "360Giving Data Standard"
            in self.browser.find_element(By.TAG_NAME, "body").text
        )
        assert (
            "360Giving data standard"
            not in self.browser.find_element(By.TAG_NAME, "body").text
        )
        self.check_js_errors()

    def test_search(self):
        server_url = reverse_lazy("home")
        self.get(server_url)
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()

        # Total number of expected grants
        assert (
            "4,649"
            in self.browser.find_element(
                By.CLASS_NAME, "search-summary-description"
            ).text
        )

        # other_currencies_modal = browser.find_element(By.ID, "other-currencies-modal")
        # search "laboratory"
        other_currencies_modal = self.browser.find_element(
            By.XPATH, "//a[@id='other-currencies-modal']/span"
        )
        assert other_currencies_modal.text == "4"
        other_currencies_modal.click()
        time.sleep(0.5)

        # browser.get_screenshot_as_file("screenshot-test_search.png")
        assert "$153,934" in self.browser.find_element(By.ID, "summary-info-model").text
        self.check_js_errors()

    def test_search_by_titles_and_descriptions_radio_button_in_search(self):
        server_url = reverse_lazy("home")
        self.get(server_url)
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        assert (
            "Titles & Descriptions"
            in self.browser.find_element(
                By.CLASS_NAME, "search-block__form-radio-group"
            ).text
        )

    def test_search_by_titles_and_descriptions(self):
        server_url = reverse_lazy("search")
        self.get(server_url)
        # search "laboratory"
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys("laboratory")

        # select title_and_description
        self.browser.find_element(By.ID, "title_and_description-label").click()
        # execute search
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()

        self.wait_for_results_page()

        self.assertIn(
            "New science laboratory",
            self.browser.find_element(
                By.CLASS_NAME, "grantnav-search__content--results"
            ).text,
        )

        self.assertIn(
            "laboratories",
            self.browser.find_element(
                By.CLASS_NAME, "grantnav-search__content--results"
            ).text,
        )

        self.assertIn(
            "Your search ‘laboratory’ returned 22 results in ‘Titles & Descriptions’",
            self.browser.find_element(By.CLASS_NAME, "search-summary-description").text,
        )

        self.get(server_url)
        # search "laboratory" in "Search All"
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys("laboratory")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()

        self.wait_for_results_page()

        self.assertIn(
            "New science laboratory",
            self.browser.find_element(By.CLASS_NAME, "grantnav-search__content--results").text
        )
        self.assertIn("laboratories", self.browser.find_element(By.CLASS_NAME, "grantnav-search__content--results").text)

        self.assertIn(
            "Your search ‘laboratory’ returned 23 results in ‘All grant fields’",
            self.browser.find_element(
                By.CLASS_NAME, "search-summary-description"
            ).text
        )

    def test_search_current_url(self):
        server_url = reverse_lazy("home")
        self.get(server_url)
        search_box = self.browser.find_element(By.ID, "text-query-input")
        search_box.send_keys("test")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()
        # Correct sorting for a text input
        url = urlparse(self.browser.current_url)
        time.sleep(3)
        path_query = f"{url.path}?{url.query}"
        self.assertTrue(path_query.startswith("/search?query=test&default_field=%2A&sort=_score+desc"),
                        f"Url was {path_query}")

    def test_empty_search(self):
        server_url = reverse_lazy("home")
        self.get(server_url)
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()
        # Check No additional params
        url = urlparse(self.browser.current_url)
        path_query = f"{url.path}?{url.query}"
        self.assertEqual(path_query, "/search?", f"Url was {path_query}")

    # This was commented out in the original tests. TODO investigate this test
    # def test_search_two_words_without_quotes(self):
    #     """
    #     When a user's search query is 2+ words without quotes,
    #     we want to inform the user that with quotes will have a better search result.
    #     """
    #     self.get(server_url)
    #     search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
    #     search_box.send_keys('social change')
    #     self.browser.find_element(By.CLASS_NAME, "large-search-button").click()

    #     assert 'If you\'re looking for a specific phrase, put quotes around it to refine your search. e.g. "youth clubs".' \
    #            in self.browser.find_element(By.TAG_NAME, 'body').text

    def test_search_two_words_with_single_quotes(self):
        server_url = reverse_lazy("home")
        self.get(server_url)
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys("'core project'")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        self.assertNotIn(
            'If you\'re looking for a specific phrase, put quotes around it to refine your search. e.g. "youth clubs".',
            self.browser.find_element(By.CLASS_NAME, "search-summary-description").text,
        )

    def test_search_two_words_with_double_quotes(self):
        server_url = reverse_lazy("search")
        self.get(server_url)
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys('"core project"')
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        self.assertNotIn(
            'If you\'re looking for a specific phrase, put quotes around it to refine your search. e.g. "youth clubs".',
            self.browser.find_element(By.CLASS_NAME, "search-summary-description").text,
        )

    def test_search_two_words_with_hyphen(self):
        """
        When a user's search query is 2 words with a hyphen,
        we want to inform the user that with quotes will have a better search result.
        """
        server_url = reverse_lazy("search")
        self.get(server_url)
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys("covid-19")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        self.assertIn(
            'If you\'re looking for a specific phrase, put quotes around it to refine your search. e.g. "youth clubs".',
            self.browser.find_element(By.ID, "search-tips").text,
        )

    def test_search_includes_and(self):
        """
        When a user's search query includes 'and', we want to inform the user of what it means.
        """
        server_url = reverse_lazy("home")
        self.get(server_url)
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys("mental and health")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        self.assertIn(
            "The AND keyword (not case-sensitive) means that results must have both words present. ",
            self.browser.find_element(By.ID, "search-tips").text,
        )

    def test_search_does_not_include_and(self):
        server_url = reverse_lazy("home")
        self.get(server_url)
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys("secondhand clothes")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        self.assertIn(
            "If you're looking for a specific phrase, put quotes around it to refine your search.",
            self.browser.find_element(By.ID, "search-tips").text,
        )

    def test_search_includes_or(self):
        """
        When a user's search query includes 'or', we want to inform the user of what it means.
        """
        server_url = reverse_lazy("home")
        self.get(server_url)
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys("mental or health")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        self.assertIn(
            "The OR keyword (not case-sensitive) means that results must have one of the words present. "
            'This is the default. If you\'re looking for a phrase that has the word "or" in '
            '(e.g. "children or adults"), put quotes around it.',
            self.browser.find_element(By.ID, "search-tips").text,
        )

    def test_search_does_not_include_or(self):
        server_url = reverse_lazy("home")
        self.get(server_url)
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys("meteor clothes")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        self.assertNotIn(
            "The OR keyword (not case-sensitive) means that results must have one of the words present. "
            'This is the default. If you\'re looking for a phrase that has the word "or" in '
            '(e.g. "children or adults"), put quotes around it.',
            self.browser.find_element(By.ID, "search-tips").text,
        )

    def test_search_display_tip(self):
        """
        When an advance search message is displayed in the search results,
        'Tip: ' will appear in front of the message.
        """
        server_url = reverse_lazy("home")
        self.get(server_url)
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys("core project")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        self.assertIn("Tip: ", self.browser.find_element(By.ID, "search-tips").text)

    def test_search_do_not_display_tip(self):
        server_url = reverse_lazy("search")
        self.get(server_url)
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys("grant")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()
        self.assertNotIn(
            "Tip: ",
            self.browser.find_element(By.CLASS_NAME, "search-summary-description").text,
        )

    def test_search_display_advanced_search_link(self):
        """
        When an advance search message is displayed in the search results,
        a link to the 'advance search' information page is also included.
        """
        server_url = reverse_lazy("home")
        self.get(server_url)
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys("core project")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        self.assertIn(
            "For more tips, see Advanced Search",
            self.browser.find_element(By.ID, "search-tips").text,
        )

    def test_search_do_not_display_advance_search_link(self):
        server_url = reverse_lazy("home")
        self.get(server_url)
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys("grant")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        self.assertNotIn(
            "For more tips, see Advanced Search",
            self.browser.find_element(By.CLASS_NAME, "search-summary-description").text
        )

    def test_bad_search(self):
        server_url = reverse_lazy("search")
        self.get(server_url)
        self.browser.find_element(By.NAME, "text_query").send_keys(" £s:::::afdsfas")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()
        not_valid = self.browser.find_element(By.ID, "not_valid").text
        assert "Search input is not valid" in not_valid
        assert "We can't find what you tried to search for." in not_valid

    def test_terms(self):
        server_url = reverse_lazy("terms")
        self.get(server_url)
        assert (
            "Terms and conditions" in self.browser.find_element(By.TAG_NAME, "h1").text
        )

    def test_title(self):
        server_url = reverse_lazy("home")
        self.get(server_url)
        assert "360Giving GrantNav" in self.browser.title

    def test_no_results_page(self):
        server_url = reverse_lazy("home")
        self.get(server_url)
        search_box = self.browser.find_element(By.CLASS_NAME, "large-search")
        search_box.send_keys("dfsergegrdtytdrthgrtyh")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        no_results = self.browser.find_element(By.ID, "no-results").text
        assert "No Results" in no_results
        assert (
            'Your search - "dfsergegrdtytdrthgrtyh" - did not match any grant records.'
            in no_results
        )

    def test_datasets_page(self):
        server_url = reverse_lazy("datasets")
        self.get(server_url)
        assert (
            "Data used in GrantNav" in self.browser.find_element(By.TAG_NAME, "h1").text
        )
        self.check_js_errors()

    def test_disclaimers(self):
        server_url = reverse_lazy("grant", args=["360G-LBFEW-111657"])
        self.get(server_url)
        assert (
            "Where is this data from"
            in self.browser.find_element(By.TAG_NAME, "body").text
        )
        self.check_js_errors()

    def test_currency_facet(self):
        server_url = reverse_lazy("home")
        self.get(server_url)
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        # Select USD
        # self.browser.get_screenshot_as_file("test2.png")
        # Open the filter group expander
        self.browser.find_element(By.ID, "filter-accordion-currency").click()
        self.browser.find_element(By.ID, "filter-option-currency-usd").click()

        # Check USD options appear
        assert "USD 0 - USD 500" in self.browser.find_element(By.TAG_NAME, "body").text

    def test_amount_awarded_facet(self):
        server_url = reverse_lazy("home")
        self.get(server_url)
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()
        # Select an amount option
        self.browser.find_element(By.ID, "amount-1000.0-5000.0").click()
        self.wait_for_results_page()
        total_grants = self.browser.find_elements(
            By.CSS_SELECTOR, ".summary-content--item span"
        )[0].text
        assert "49" in total_grants, "Expected number of grants not found"

    def test_county_location_facet(self):
        server_url = reverse_lazy("search")
        self.get(server_url)

        # Open county
        self.browser.find_element(By.ID, "filter-accordion-ukcounty").click()
        self.browser.find_element(By.ID, "filter-option-ukcounty-liverpool").click()

        total_grants = self.browser.find_elements(
            By.CSS_SELECTOR, ".summary-content--item span"
        )[0].text

        assert (
            "11" in total_grants
        ), f"Expected total grants not found for county liverpool, got {total_grants} instead of 9"

    def test_zero_grant_info_link_absent(self):
        server_url = reverse_lazy("grant", args=["360G-LBFEW-99233"])
        self.get(server_url)
        assert len(self.browser.find_elements(By.ID, "zero_value_grant_help_link")) == 0

    def test_search_recipients(self):
        server_url = reverse_lazy("recipients")
        self.get(server_url)

        self.browser.find_element(By.NAME, "text_query").send_keys("Social Justice")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        # self.browser.get_screenshot_as_file("recipients-search.png")

        self.assertEqual(
            len(
                self.browser.find_elements(
                    By.CLASS_NAME, "grant-search-result__recipients"
                )
            ),
            20,
        )
        self.check_js_errors()

    def test_search_funders(self):
        server_url = reverse_lazy("funders")
        self.get(server_url)

        self.browser.find_element(By.NAME, "text_query").send_keys("foundation")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        # self.browser.get_screenshot_as_file("recipients-search.png")

        self.assertEqual(
            len(
                self.browser.find_elements(
                    By.CLASS_NAME, "grant-search-result__funders"
                )
            ),
            20,
        )
        self.check_js_errors()

    def test_search_funders_amount_order(self):
        """ Test to make sure that the funders results react to the ordering as set """

        def _gbp_to_float(text):
            """ returns float version of text e.g. "£12,233.00" -> 122333.00 """
            return float(text.replace("£", "").replace(",", ""))

        SORT_ID = "sort_options"
        RESULT_EL_SELECTOR = "[data-testid='result-funder-total-amount-recipient_org']"

        # £ High to Low #####
        server_url = reverse_lazy("funders")
        self.get(server_url)

        select = Select(self.browser.find_element(By.ID, SORT_ID))
        select.select_by_visible_text("Total GBP Amount to Organisations - Highest First")

        self.wait_for_results_page()

        amount_elements = self.browser.find_elements(By.CSS_SELECTOR, RESULT_EL_SELECTOR)

        # Get the first result item
        prev_amount = _gbp_to_float(amount_elements[0].text)
        # Make sure the amounts in the results are in descending order
        for amount_el in amount_elements[1:]:
            amount = _gbp_to_float(amount_el.text)
            self.assertTrue(amount < prev_amount, f"{amount} < {prev_amount}")
            prev_amount = amount

        # £ Low to high #####
        server_url = reverse_lazy("funders")
        self.get(server_url)

        select = Select(self.browser.find_element(By.ID, SORT_ID))
        select.select_by_visible_text("Total GBP Amount to Organisations - Lowest First")

        self.wait_for_results_page()

        amount_elements = self.browser.find_elements(By.CSS_SELECTOR, RESULT_EL_SELECTOR)

        # Get the first result item
        prev_amount = _gbp_to_float(amount_elements[0].text)
        # Make sure the amounts in the results are in ascending order
        for amount_el in amount_elements[1:]:
            amount = _gbp_to_float(amount_el.text)
            self.assertTrue(amount > prev_amount, f"{amount} > {prev_amount}")
            prev_amount = amount

    def test_funders_alphabetical_sort_a_to_z(self):
        """Test alphabetical sort A-Z on Funder search page"""
        server_url = reverse_lazy("funders")
        self.get(server_url)

        # Perform initial search
        self.browser.find_element(By.NAME, "text_query").send_keys("foundation")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        # Select alphabetical sort A-Z
        select = Select(self.browser.find_element(By.ID, "sort_options"))
        select.select_by_visible_text("Name - Alphabetical (A-Z)")
        self.wait_for_results_page()

        # Get the funder names from the results
        funder_elements = self.browser.find_elements(
            By.CLASS_NAME, "grant-search-result__title"
        )
        funder_names = [elem.text for elem in funder_elements]

        # Verify that at least some results are present
        self.assertGreater(len(funder_names), 0, "No funder results found")

        # Verify sorting is alphabetical (A-Z)
        sorted_names = sorted(funder_names)
        self.assertEqual(
            funder_names,
            sorted_names,
            f"Funder names not in alphabetical order. Got: {funder_names}, Expected: {sorted_names}",
        )
        self.check_js_errors()

    def test_funders_alphabetical_sort_z_to_a(self):
        """Test alphabetical sort Z-A on Funder search page"""
        server_url = reverse_lazy("funders")
        self.get(server_url)

        # Perform initial search
        self.browser.find_element(By.NAME, "text_query").send_keys("foundation")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        # Select alphabetical sort Z-A
        select = Select(self.browser.find_element(By.ID, "sort_options"))
        select.select_by_visible_text("Name - Alphabetical (Z-A)")
        self.wait_for_results_page()

        # Get the funder names from the results
        funder_elements = self.browser.find_elements(
            By.CLASS_NAME, "grant-search-result__title"
        )
        funder_names = [elem.text for elem in funder_elements]

        # Verify that at least some results are present
        self.assertGreater(len(funder_names), 0, "No funder results found")

        # Verify sorting is reverse alphabetical (Z-A)
        reverse_sorted_names = sorted(funder_names, reverse=True)
        self.assertEqual(
            funder_names,
            reverse_sorted_names,
            f"Funder names not in reverse alphabetical order. Got: {funder_names}, Expected: {reverse_sorted_names}",
        )
        self.check_js_errors()

    def test_recipients_alphabetical_sort_a_to_z(self):
        """Test alphabetical sort A-Z on Recipient search page"""
        server_url = reverse_lazy("recipients")
        self.get(server_url)

        # Perform initial search
        self.browser.find_element(By.NAME, "text_query").send_keys("Social Justice")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        # Select alphabetical sort A-Z
        select = Select(self.browser.find_element(By.ID, "sort_options"))
        select.select_by_visible_text("Name - Alphabetical (A-Z)")
        self.wait_for_results_page()

        # Get the recipient names from the results
        recipient_elements = self.browser.find_elements(
            By.CLASS_NAME, "grant-search-result__title"
        )
        recipient_names = [elem.text for elem in recipient_elements]

        # Verify that at least some results are present
        self.assertGreater(len(recipient_names), 0, "No recipient results found")

        # Verify sorting is alphabetical (A-Z)
        sorted_names = sorted(recipient_names)
        self.assertEqual(
            recipient_names,
            sorted_names,
            f"Recipient names not in alphabetical order. Got: {recipient_names}, Expected: {sorted_names}",
        )
        self.check_js_errors()

    def test_recipients_alphabetical_sort_z_to_a(self):
        """Test alphabetical sort Z-A on Recipient search page"""
        server_url = reverse_lazy("recipients")
        self.get(server_url)

        # Perform initial search
        self.browser.find_element(By.NAME, "text_query").send_keys("Social Justice")
        self.browser.find_element(By.CLASS_NAME, "large-search-button").click()
        self.wait_for_results_page()

        # Select alphabetical sort Z-A
        select = Select(self.browser.find_element(By.ID, "sort_options"))
        select.select_by_visible_text("Name - Alphabetical (Z-A)")
        self.wait_for_results_page()

        # Get the recipient names from the results
        recipient_elements = self.browser.find_elements(
            By.CLASS_NAME, "grant-search-result__title"
        )
        recipient_names = [elem.text for elem in recipient_elements]

        # Verify that at least some results are present
        self.assertGreater(len(recipient_names), 0, "No recipient results found")

        # Verify sorting is reverse alphabetical (Z-A)
        reverse_sorted_names = sorted(recipient_names, reverse=True)
        self.assertEqual(
            recipient_names,
            reverse_sorted_names,
            f"Recipient names not in reverse alphabetical order. Got: {recipient_names}, Expected: {reverse_sorted_names}",
        )
        self.check_js_errors()

    def test_org_page(self):
        server_url = reverse_lazy("org", args=["GB-CHC-1156077"])
        self.get(server_url)
        # self.browser.get_screenshot_as_file("org-page.png")

        assert "Wolfson Foundation" in self.browser.find_element(By.TAG_NAME, "h1").text
        self.check_js_errors()

    def test_insights_button(self):
        """Tests that the insights button takes us to an Insights site"""

        for button in self.browser.find_elements(
            By.CSS_SELECTOR, "a[data='insights-integration-btn']"
        ):
            # Narrow search results to fewer than 10k
            server_url = reverse_lazy("search")
            self.get(f"{server_url}?currency=AUD")
            button.click()
            assert self.browser.find_element(By.TAG_NAME, "title").text == "360Insights"
            # Clear self.browser log for external site
            self.browser.get_log("self.browser")
