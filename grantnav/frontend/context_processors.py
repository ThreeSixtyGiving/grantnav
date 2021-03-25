from django.conf import settings


def piwik(request):
    return {'piwik': settings.PIWIK}


def navigation(request):
    sections = [
        {"name": "About the data", "url": "https://help.grantnav.threesixtygiving.org/en/latest/data.html", "id": "about_link"},
        {"name": "Get Help", "url": "https://help.grantnav.threesixtygiving.org/", "id": "help_link"},
    ]
    return {'nav_menu': sections}
