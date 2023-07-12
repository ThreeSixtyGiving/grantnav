from django.conf.urls import url

import grantnav.api.aggregates

app_name = "api"

urlpatterns = [
    url("aggregates/search", grantnav.api.aggregates.Search.as_view(), name="insights-search"),
]