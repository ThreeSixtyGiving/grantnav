from django.conf import settings


def piwik(request):
    return {'piwik': settings.PIWIK}


def navigation(request):
    sections = [
        {"name": "Get Help", "url": "/help", "id": "help_link"},
        {"name": "Forum", "url": "https://forum.threesixtygiving.org/c/grantnav/8", "id": "forum_link"}
    ]
    return {'nav_menu': sections}
