from django.conf import settings


def piwik(request):
    return {'piwik': settings.PIWIK}


def navigation(request):
    sections = [
        {"name": "About the data", "url": "http://grantnav-dev.default.threesixtygiving.uk0.bigv.io/about", "id": "about_link"},
        {"name": "Forum", "url": "https://forum.threesixtygiving.org/c/grantnav/8", "id": "forum_link"},
        {"name": "Get Help", "url": "https://help.grantnav.threesixtygiving.org/", "id": "help_link"},
    ]
    return {'nav_menu': sections}
