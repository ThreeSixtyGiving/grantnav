from django.conf import settings


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
