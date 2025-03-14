from django.urls import path
import grantnav.api.aggregates

app_name = "api"

urlpatterns = [
    path("aggregates/search", grantnav.api.aggregates.Search.as_view(), name="aggregates"),
]
