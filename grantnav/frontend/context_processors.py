import os.path

from django.conf import settings
from os.path import getmtime


def piwik(request):
    return {'piwik': settings.PIWIK}


def navigation(request):
    sections = [
        {"name": "About 360Giving", "url": "https://www.threesixtygiving.org/",
         "id": "about_threesixty_link"},
        {"name": "About the data", "url": "https://help.grantnav.threesixtygiving.org/en/latest/data.html", "id": "about_link"},
        {"name": "Get Help", "url": "https://help.grantnav.threesixtygiving.org/", "id": "help_link"},
    ]
    return {'nav_menu': sections}


# This is calculated here and not in the main_css_cache_key() function so that it is only checked once per process.
# Checking once per request is an unnecessary performance hit.
MAIN_CSS_CACHE_KEY = getmtime(os.path.join(settings.BASE_DIR, 'grantnav', 'frontend', 'static', 'css', 'main.css'))


def main_css_cache_key(request):
    return {'main_css_cache_key': MAIN_CSS_CACHE_KEY}
