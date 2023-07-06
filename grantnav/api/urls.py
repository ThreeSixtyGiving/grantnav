from django.conf.urls import url

import grantnav.api.insights

app_name = "api"

urlpatterns = [
    url("insights/search", grantnav.api.insights.Search.as_view(), name="insights-search"),
]