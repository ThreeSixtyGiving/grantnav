from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.search, name='search'),
    url(r'^grant/(.*)$', views.grant, name='grant'),
    url(r'^stats', views.stats, name='stats'),
]
