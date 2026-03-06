# These settings redirect the matomo analytics to a local dev instance
# Helpful for developing the analytics code

from .settings import * # noqaa

DEBUG = True

SECRET_KEY = 'itsasecret'

PIWIK = {
    'url': "//localhost:8090/",
    'site_id': '1',
    'cookie_domain': '',
    'cookie_subdomains': False,
}

INSIGHTS_BASE_URL = "http://localhost:8081"

DISABLE_COOKIE_POPUP = False
