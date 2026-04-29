import os
import requests
import time
import urllib3

from tests.browser_test_case import BrowserTestCase

from django.test import override_settings, tag
from django.urls import reverse_lazy

from selenium.webdriver.common.by import By

prefix = os.path.join(os.path.dirname(__file__), "data")


urllib3.disable_warnings()


@tag("link-runner")
@override_settings(
    PROVENANCE_JSON=os.path.join(prefix, "data.json"), DISABLE_COOKIE_POPUP=True
)
class LinkCheckTests(BrowserTestCase):
    def test_links(self):
        """Load each path and check the links within the page respond HTTP success"""

        links_checked = {}

        def is_blocked_by_cloudflare(response: requests.Response) -> bool:
            # Check for characteristic headers.
            if (
                "cloudflare" in response.headers.get("Server", "").lower()
                or "CF-RAY" in response.headers
            ):
                return True

            return False

        def check_single_link(link: str) -> int:
            try:
                # Some sites reject connection without a user agent.
                DEFAULT_HEADERS = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
                }

                # First, just try a head request.  If this is anything but a 403 then return the status code.
                r = requests.head(link, headers=DEFAULT_HEADERS, verify=False)
                if r.status_code != 403:
                    return r.status_code

                # We have received 403 unauthorised and need to try again.  Delay by two seconds and try again
                # with GET which might look less suspicious but using stream=True still has a low impact.
                time.sleep(2)
                r = requests.get(
                    link, headers=DEFAULT_HEADERS, verify=False, stream=True
                )
                if r.status_code != 403:
                    return r.status_code

                # Skip the test if we are blocked by Cloudflare.
                if is_blocked_by_cloudflare(r):
                    print(f"{link} is blocked by Cloudflare - skipping")
                    return 200

                return r.status_code

            except Exception:
                # Set status code to 0 (not a HTTP response code) so it gets displayed along with the other errors at the end.
                # This is usually triggered by the request timing out.
                return 0

            return 0

        def check_page_for_broken_links(page):
            # We use selenium for this kind of test because it's a convenient way to manipulate the dom
            self.get(page)

            links = []
            # Skip some sites that are are behind cloudflare or other services which blocks the script
            skip = [
                "#",
                "https://twitter.com/360Giving/",
                "https://insights.threesixtygiving.org/?url=https://grantnav.threesixtygiving.org/search.json%3F",
                "https://www.parliament.uk/site-information/copyright/open-parliament-licence",
                "https://www.ons.gov.uk/",
                "https://www.oscr.org.uk/",
                "https://www.hesa.ac.uk/",
                "https://digital.nhs.uk/",
                "https://www.gnu.org/licenses/",
            ]

            for a in self.browser.find_elements(By.TAG_NAME, "a"):
                # Datatables quirk with empty <a> tags, select2 quirk with same issue
                if (
                    a.get_attribute("aria-controls")
                    or a.get_attribute("class") == "remove-select2-option"
                ):
                    continue

                link = a.get_attribute("href")

                assert (
                    link is not None
                ), f"Error An <a> tag without a href attribute on {page} {a.get_attribute('outerHTML')}"

                if link not in skip:
                    links.append(link)

            broken = False
            for link in links:

                if link not in links_checked.keys():

                    status_code = check_single_link(link)
                    links_checked[link] = status_code
                    if status_code < 200 or status_code > 399:
                        broken = True

            errors = ", ".join(
                [
                    f"{link} ({status})"
                    for link, status in links_checked.items()
                    if status < 200 or status > 399
                ]
            )
            print(errors)
            assert not broken, f"Links broken on page {page}: {errors}"

        pages_to_find_links = [
            reverse_lazy("home"),
            reverse_lazy("search") + "?sort=amountAwarded+desc",
            reverse_lazy("funders"),
            reverse_lazy("recipients"),
            reverse_lazy("about"),
            reverse_lazy("datasets"),
            reverse_lazy("grant", args=["360G-LBFEW-99233"]),  # regular grant
            reverse_lazy("grant", args=["360G-LBFEW-94200"]),
            reverse_lazy("org", args=["GB-CHC-1126147"]),
        ]

        # Test the pages that has the links on to be tested
        for page in pages_to_find_links:
            r = requests.head(f"{self.live_server_url}{page}")
            status_code = r.status_code
            self.assertFalse(
                (status_code < 200 or status_code > 399),
                f"{self.live_server_url}{page} error {status_code}",
            )

        # Test the links on the pages
        for page in pages_to_find_links:
            check_page_for_broken_links(page)
