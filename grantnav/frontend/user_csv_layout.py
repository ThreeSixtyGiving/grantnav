from django.http import HttpResponse
from . import views
import json


# Process the custom download request
def process(request):
    fields = json.loads(request.GET.get("selection"))
    # TODO checks on this incoming data
    return views.grants_csv_paged(
        json.loads(request.GET.get("json_query")),
        grant_csv_titles=[item["title"] for item in fields],
        grant_csv_paths=[item["path"] for item in fields],
    )
