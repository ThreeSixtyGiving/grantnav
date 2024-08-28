from django.http import Http404
from . import views
import json
from grantnav.csv_layout import grants_csv_dict


# Process the custom download request
def process(request):
    fields = json.loads(request.GET.get("selection"))

    # Check the incoming data is known to us
    for field in fields:
        if grants_csv_dict.get(field["path"]) is not field["title"]:
            raise Http404("The field(s) requested are not available.")

    return views.grants_csv_paged(
        json.loads(request.GET.get("json_query")),
        grant_csv_titles=[item["title"] for item in fields],
        grant_csv_paths=[item["path"] for item in fields],
    )
