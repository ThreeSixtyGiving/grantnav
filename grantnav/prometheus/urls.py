from django.conf.urls import url

import grantnav.prometheus.views

app_name = "prometheus"

urlpatterns = [
    url("metrics", grantnav.prometheus.views.ServiceMetrics.as_view(), name="service-metrics"),
]
