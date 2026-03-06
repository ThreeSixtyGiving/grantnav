import os.path
import datetime

from django.conf import settings


def matomo(request):
    return {'matomo': settings.PIWIK}


def navigation(request):
    sections = [
        {"name": "About 360Giving", "url": "https://www.360giving.org/", "id": "about_threesixty_link"},
        {"name": "Before you start", "url": "https://www.360giving.org/explore/before-you-start/", "id": "about_link"},
        {"name": "How to search", "url": "https://www.360giving.org/explore/how-to-search/", "id": "how_to_search_link"},
        {"name": "GrantNav user guide", "url": "https://www.360giving.org/explore/user-guide/", "id": "help_link"},
    ]
    return {'nav_menu': sections}


# This is calculated here and not in the main_css_cache_key() function so that it is only checked once per process.
# Checking once per request is an unnecessary performance hit.
MAIN_CSS_CACHE_KEY = os.path.getmtime(os.path.join(settings.BASE_DIR, 'grantnav', 'frontend', 'static', 'css', 'main.css'))


def main_css_cache_key(request):
    return {'main_css_cache_key': MAIN_CSS_CACHE_KEY}


def debug_mode(request):
    return {"debug": settings.DEBUG}


def insights_url(request):
    return {"insights_base_url": settings.INSIGHTS_BASE_URL}


def disable_cookie_popup(request):
    return {"disable_cookie_popup": settings.DISABLE_COOKIE_POPUP}


def current_year(request):
    return {"current_year": datetime.datetime.now().year}
