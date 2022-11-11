from django.conf.urls import url

from . import views
from . import recipients_search_view
from . import funders_search_view
from django.views.generic import TemplateView
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^search$', views.search, name='search'),
    url(r'^widgets', views.search, {'template_name': 'search_widgets.html'}, name='search.widgets'),
    url(r'^widgets.api', views.search_wrapper_xframe_exempt, name='widgets.api'),
    url(r'^tabular', views.search_wrapper_xframe_exempt, {'template_name': 'widgets/tabular_grants.html'}, name='widgets.tabular'),
    url(r'^amount_graph', views.search_wrapper_xframe_exempt, {'template_name': 'widgets/amount_graph.html'}, name='widgets.amount_graph'),
    url(r'^date_graph', views.search_wrapper_xframe_exempt, {'template_name': 'widgets/date_graph.html'}, name='widgets.date_graph'),
    url(r'^search\.csv$', views.search, name='search.csv'),
    url(r'^search\.json$', views.search, name='search.json'),
    url(r'^search\.json$', views.search, name='search.json'),
    url(r'^filter_search_ajax$', views.filter_search_ajax, name='filter_search_ajax'),
    url(r'^grant/(.*)$', views.grant, name='grant'),
    url(r'^grants_datatables$', views.grants_datatables, name='grants_datatables'),
    url(r'^funder_recipients_datatables$', views.funder_recipients_datatables, name='funder_recipients_datatables'),
    url(r'^funder_recipients_datatables.csv$', views.funder_recipients_datatables, name='funder_recipients_datatables.csv'),
    url(r'^funder_recipients_datatables.json$', views.funder_recipients_datatables, name='funder_recipients_datatables.json'),
    url(r'^funders_datatables$', views.funders_datatables, name='funders_datatables'),
    url(r'^funders_datatables.csv$', views.funders_datatables, name='funders_datatables.csv'),
    url(r'^funders_datatables.json$', views.funders_datatables, name='funders_datatables.json'),
    url(r'^recipients', recipients_search_view.search, name='recipients'),
    url(r'^funders', funders_search_view.search, name='funders'),
    url(r'^org/(.*)$', views.org, name='org'),
    url(r'^region/(.*)$', views.region, name='region'),
    url(r'^region/(.*)\.csv$', views.region, name='region.csv'),
    url(r'^region/(.*)\.json$', views.region, name='region.json'),
    url(r'^district/(.*)$', views.district, name='district'),
    url(r'^district/(.*)\.csv$', views.district, name='district.csv'),
    url(r'^district/(.*)\.json$', views.district, name='district.json'),
    url(r'^datasets/$', views.datasets, name='datasets'),
    url(r'^take_down_policy', TemplateView.as_view(template_name='take_down_policy.html'), name='take_down_policy'),
    url(r'^terms', TemplateView.as_view(template_name='terms.html'), name='terms'),
    url(r'^about', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^api/grants.json', views.api_grants, name='api.grants.json'),
    url(r'^api/grants.csv', views.api_grants, name='api.grants.csv'),
    # Redirects
    url(r'^publisher/(.*)$', views.publisher, name='publisher'),
    url(r'^recipient/(.*)$', views.recipient, name='recipient'),
    url(r'^funder/(.*)$', views.recipient, name='recipient'),
    url(r'^help', RedirectView.as_view(url="https://help.grantnav.threesixtygiving.org/"), name="help"),
    # Developers content used to live on this website but it was then moved to an external help site.
    # Redirect people to make sure any old links continue to work.
    url(r'^developers', RedirectView.as_view(url="https://help.grantnav.threesixtygiving.org/en/latest/developers.html"), name='developers'),
]
