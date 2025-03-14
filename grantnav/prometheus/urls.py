from django.urls import path
import grantnav.prometheus.views

app_name = "prometheus"

urlpatterns = [
    path("metrics", grantnav.prometheus.views.ServiceMetrics.as_view(), name="service-metrics"),
]
