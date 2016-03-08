from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.search, name='search'),
    url(r'^grant/(.*)$', views.grant, name='grant'),
    url(r'^funder/(.*)$', views.funder, name='funder'),
    url(r'^funder_recipients_datatables$', views.funder_recipients_datatables, name='funder_recipients_datatables'),
    url(r'^funder_grants_datatables$', views.funder_grants_datatables, name='funder_grants_datatables'),
    url(r'^recipient/(.*)$', views.recipient, name='recipient'),
    url(r'^recipient_grants_datatables$', views.recipient_grants_datatables, name='recipient_grants_datatables'),
    url(r'^stats', views.stats, name='stats'),
]
