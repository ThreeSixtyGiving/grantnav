from django.shortcuts import render, redirect
from grantnav.search import get_es
from django.utils.http import urlencode
import json
import copy
import math

BASIC_QUERY = {"query": {"bool": {"must": {"query_string": {"query": "", "fields": ["_all"]}}}},
               "aggs": {
                   "fundingOrg": {"terms": {"field": "fundingOrganization.whole_name"}},
                   "recipientOrg": {"terms": {"field": "recipientOrganization.whole_name"}}
               }}
SIZE = 10

def get_pagination(request, context, page):
    total_pages = math.ceil(context['results']['hits']['total'] / SIZE)
    if page < total_pages:
        context['next_page'] = request.path + '?' + urlencode({"json_query": context['json_query'], 'page': page + 1})
    if page != 1 and total_pages > 1:
        context['prev_page'] = request.path + '?' + urlencode({"json_query": context['json_query'], 'page': page - 1})


def search(request):
    context = {}
    json_query = request.GET.get('json_query') or ""
    try:
        json_query = json.loads(json_query)
    except ValueError:
        json_query = {}

    text_query = request.GET.get('text_query')
    if text_query is not None:
        json_query = json_query
        try:
            json_query["query"]["bool"]["must"]["query_string"]["query"] = text_query
        except KeyError:
            json_query = copy.deepcopy(BASIC_QUERY)
            json_query["query"]["bool"]["must"]["query_string"]["query"] = text_query
        return redirect(request.path + '?' + urlencode({"json_query": json.dumps(json_query)}))

    es = get_es()
    results = None
    if json_query:
        try:
            page = int(request.GET.get('page', 1))
            if page < 1:
                page = 1
        except ValueError:
            page = 1

        results = es.search(body=json_query, size=SIZE, from_=(page - 1) * SIZE)
        try:
            context['text_query'] = json_query["query"]["bool"]["must"]["query_string"]["query"]
        except KeyError:
            json_query = copy.deepcopy(BASIC_QUERY)
            json_query["query"]["bool"]["must"]["query_string"]["query"] = text_query
        context['json_query'] = json.dumps(json_query)
        context['results'] = results
        get_pagination(request, context, page)

    return render(request, "search.html", context=context)
