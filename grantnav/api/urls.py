from django.urls import re_path
import grantnav.api.aggregates

app_name = "api"

urlpatterns = [
    re_path(r"^aggregates/search", grantnav.api.aggregates.Search.as_view(), name="aggregates"),
]
