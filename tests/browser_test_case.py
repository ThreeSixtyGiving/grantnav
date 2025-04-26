import os
import time

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from dataload.import_to_elasticsearch import import_to_elasticsearch

# Test data directory
prefix = os.path.join(os.path.dirname(__file__), "data")


class BrowserTestCase(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        import_to_elasticsearch(
            [
                os.path.join(prefix, "a002400000KeYdsAAF-currency.json"),
                os.path.join(prefix, "a002400000OiDBQAA3.json"),
                os.path.join(prefix, "awefw001p00000zgyHZAAY.json"),
            ],
            clean=True,
            funders=os.path.join(prefix, "funders.jsonl"),
            recipients=os.path.join(prefix, "recipients.jsonl"),
        )
        # elastic search needs some time to commit its data
        time.sleep(5)

    def setUp(self, *args, **kwargs):
        BROWSER = os.environ.get("BROWSER", "ChromeHeadless")

        if BROWSER == "ChromeHeadless":
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            # no-sandbox prevents an error when running as the root user
            chrome_options.add_argument("--no-sandbox")
            # uncomment this if "DevToolsActivePort" error / ubuntu snap workaround
            chrome_options.add_argument("--remote-debugging-port=9222")
            # chrome_options.add_argument('ignore-unexpected-deprecations')
            self.browser = webdriver.Chrome(options=chrome_options)
        elif BROWSER == "Firefox" or BROWSER == "FirefoxHeadless":
            # While we can technically run the tests in Firefox, they won't pass
            # because the self.browser.get_log() method used here to get browser console logs
            # is non-standard and only implement by ChromeDriver.
            # See: https://github.com/mozilla/geckodriver/issues/330
            ff_options = webdriver.FirefoxOptions()
            if BROWSER == "FirefoxHeadless":
                ff_options.add_argument("-headless")
            # Make downloads work
            ff_options.set_preference("browser.download.folderList", 2)
            ff_options.set_preference("browser.download.manager.showWhenStarting", False)
            ff_options.set_preference("browser.download.dir", os.getcwd())
            ff_options.set_preference(
                "browser.helperApps.neverAsk.saveToDisk", "application/json"
            )
            self.browser = webdriver.Firefox(options=ff_options)
        else:
            self.browser = getattr(webdriver, BROWSER)()
        # Make sure we wait 5 seconds at least before slenium delcares the element no existent
        self.browser.implicitly_wait(5)

    def tearDown(self):
        self.browser.quit()

    def get(self, path):
        """convenience function load the browser at a given path"""
        self.browser.get(f"{self.live_server_url}{path}")

    def check_js_errors(self):
        for log in self.browser.get_log("browser"):
            # TODO Datatables is sending warnings that we can't currently fix
            if "datatables" in str(log).lower():
                print(
                    f"Skipping datatables warning {self.browser.current_url} : f{log}"
                )
                continue
            assert "SEVERE" not in log["level"], f"{self.browser.current_url} : {log} "
        # Clear log so that we know which test was the first to come across this issue
        # otherwise the browser log is persistent.
        self.browser.get_log("browser")
