from django.shortcuts import render, redirect
from grantnav.search import get_es
from django.utils.http import urlencode
from django.conf import settings
import jsonref
import json
import copy
import math
import collections

BASIC_QUERY = {"query": {"bool":
                             {"must": {"query_string": {"query": ""}},
                              "filter": {}}
               },
               "aggs": {
                   "fundingOrganization": {"terms": {"field": "fundingOrganization.whole_name"}},
                   "recipientOrganization": {"terms": {"field": "recipientOrganization.whole_name"}}
               }}
SIZE = 10

def get_pagination(request, context, page):
    total_pages = math.ceil(context['results']['hits']['total'] / SIZE)
    if page < total_pages:
        context['next_page'] = request.path + '?' + urlencode({"json_query": context['json_query'], 'page': page + 1})
    if page != 1 and total_pages > 1:
        context['prev_page'] = request.path + '?' + urlencode({"json_query": context['json_query'], 'page': page - 1})

def get_facets(request, context, json_query):
    try:
        current_filter = json_query["query"]["bool"]["filter"]
    except KeyError:
        current_filter = {}
        json_query["query"]["bool"] = {}

    current_and = current_filter.get("and", [])
    if current_and:
        json_query["query"]["bool"]["filter"] = {}
        context["results"]["clear_all_facet_url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})

    aggregate_to_field = {agg_name: agg["terms"]["field"] for agg_name, agg in json_query["aggs"].items()}

    for aggregation, result in context["results"]["aggregations"].items():
        field_name = aggregate_to_field[aggregation]
        for bucket in result['buckets']:
            facet_value = bucket['key']
            new_filter = copy.deepcopy(current_filter)
            new_filter.get("and", [])
            new_filter_terms = collections.defaultdict(list)
            for filter in new_filter.get("and", []):
                field, value = filter["term"].copy().popitem()
                new_filter_terms[field].append(value)

            filter_values = new_filter_terms.get(field_name)
            if filter_values is None:
                filter_values = []
                new_filter_terms[field_name] = filter_values
            if facet_value in filter_values:
                bucket["selected"] = True
                filter_values.remove(facet_value)
                if not filter_values:
                    new_filter_terms.pop(field_name)
            else:
                filter_values.append(facet_value)
            new_and = []
            for field, values in new_filter_terms.items():
                new_and.extend({"term": { field : value }} for value in values)
            new_filter["and"] = new_and
            if not new_filter["and"]:
                new_filter.pop("and")
            json_query["query"]["bool"]["filter"] = new_filter
            bucket["url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})
        if current_and:
            new_filter = copy.deepcopy(current_filter)
            filter_terms = collections.defaultdict(list)
            for filter in new_filter.get("and", []):
                field, value = filter["term"].copy().popitem()
                filter_terms[field].append(value)
            if field_name in filter_terms:
                new_and = []
                for field, values in filter_terms.items():
                    new_and.extend({"term": { field : value }} for value in values if field != field_name)
                new_filter["and"] = new_and
                if not new_filter["and"]:
                    new_filter.pop("and")
                json_query["query"]["bool"]["filter"] = new_filter
                result['clear_url'] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})

def search(request):
    context = {}
    json_query = request.GET.get('json_query') or ""
    try:
        json_query = json.loads(json_query)
    except ValueError:
        json_query = {}

    text_query = request.GET.get('text_query')
    if text_query is not None:
        if text_query == '':
            text_query = '*'
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

        results = es.search(body=json_query, size=SIZE, from_=(page - 1) * SIZE, index="threesixtygiving")
        try:
            context['text_query'] = json_query["query"]["bool"]["must"]["query_string"]["query"]
        except KeyError:
            json_query = copy.deepcopy(BASIC_QUERY)
            json_query["query"]["bool"]["must"]["query_string"]["query"] = text_query
        if context['text_query'] == '*':
            context['text_query'] = ''
        context['results'] = results
        context['json_query'] = json.dumps(json_query)
        get_facets(request, context, json_query)
        get_pagination(request, context, page)

    return render(request, "search.html", context=context)
