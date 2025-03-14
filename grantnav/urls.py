"""grantnav URL Configuration"""

from django.urls import include, path

urlpatterns = [
    path('', include('grantnav.frontend.urls')),
    path('prometheus/', include('grantnav.prometheus.urls')),
    path('api/', include('grantnav.api.urls')),
]
