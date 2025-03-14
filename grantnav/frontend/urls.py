from django.urls import path, re_path
from . import views
from . import recipients_search_view
from . import funders_search_view
from . import user_csv_layout
from django.views.generic import TemplateView
from django.views.generic import RedirectView


urlpatterns = [
    path('', views.home, name='home'),
    path('search', views.search, name='search'),
    path('widgets', views.search, {'template_name': 'search_widgets.html'}, name='search.widgets'),
    path('widget-render/tabular', views.search_wrapper_xframe_exempt, {'template_name': 'widgets/tabular_grants.html'}, name='widgets.tabular'),
    path('widget-render/amount_graph', views.search_wrapper_xframe_exempt, {'template_name': 'widgets/amount_graph.html'}, name='widgets.amount_graph'),
    path('widget-render/date_graph', views.search_wrapper_xframe_exempt, {'template_name': 'widgets/date_graph.html'}, name='widgets.date_graph'),
    re_path(r'^search\.widgets_api', views.search_wrapper_xframe_exempt, name='search.widgets_api'),
    re_path(r'^search\.csv$', views.search, name='search.csv'),
    re_path(r'^search\.json$', views.search, name='search.json'),
    re_path(r'^search\.json$', views.search, name='search.json'),
    path('filter_search_ajax', views.filter_search_ajax, name='filter_search_ajax'),
    re_path(r'^grant/(.*)$', views.grant, name='grant'),
    path('grants_datatables', views.grants_datatables, name='grants_datatables'),
    path('funder_recipients_datatables', views.funder_recipients_datatables, name='funder_recipients_datatables'),
    path('funder_recipients_datatables.csv', views.funder_recipients_datatables, name='funder_recipients_datatables.csv'),
    path('funder_recipients_datatables.json', views.funder_recipients_datatables, name='funder_recipients_datatables.json'),
    path('funders_datatables', views.funders_datatables, name='funders_datatables'),
    path('funders_datatables.csv', views.funders_datatables, name='funders_datatables.csv'),
    path('funders_datatables.json', views.funders_datatables, name='funders_datatables.json'),
    path('recipients', recipients_search_view.search, name='recipients'),
    path('funders', funders_search_view.search, name='funders'),
    re_path(r'^org/(.*)$', views.org, name='org'),
    re_path(r'^region/(.*)$', views.region, name='region'),
    re_path(r'^region/(.*)\.csv$', views.region, name='region.csv'),
    re_path(r'^region/(.*)\.json$', views.region, name='region.json'),
    re_path(r'^district/(.*)$', views.district, name='district'),
    re_path(r'^district/(.*)\.csv$', views.district, name='district.csv'),
    re_path(r'^district/(.*)\.json$', views.district, name='district.json'),
    path('datasets/', views.datasets, name='datasets'),
    path('terms', TemplateView.as_view(template_name='terms.html'), name='terms'),
    path('about', TemplateView.as_view(template_name='about.html'), name='about'),
    path('search_custom.csv', user_csv_layout.process, name="custom_download"),
    # Redirects
    path('individuals', views.individuals, name="individuals"),
    re_path(r'^publisher/(.*)$', views.publisher, name='publisher'),
    re_path(r'^recipient/(.*)$', views.recipient, name='recipient'),
    re_path(r'^funder/(.*)$', views.funder, name='funder'),
    path('help', RedirectView.as_view(url="https://www.360giving.org/explore/user-guide/"), name="help"),
    path('take_down_policy', RedirectView.as_view(url="https://www.360giving.org/legal-policies/take-down-policy/"), name='take_down_policy'),
    # Developers content used to live on this website but it was then moved to an external help site.
    # Redirect people to make sure any old links continue to work.
    path('developers', RedirectView.as_view(url="https://www.360giving.org/explore/technical/"), name='developers'),
]
