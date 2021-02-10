from django.conf import settings


def piwik(request):
    return {'piwik': settings.PIWIK}

def navigation(request):
    sections = [
        {"name": "Get Help", "url": "/help"}, 
        {"name": "Forum", "url": "https://forum.threesixtygiving.org/c/grantnav/8"}
    ]
    return {'nav_menu': sections}
