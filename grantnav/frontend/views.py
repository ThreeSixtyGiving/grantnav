from django.shortcuts import render, redirect
from grantnav.search import get_es
from django.utils.http import urlencode
from django.conf import settings
import elasticsearch.exceptions
import jsonref
import json
import copy
import math
import collections

BASIC_QUERY = {"query": {"bool": {"must":
                  {"query_string": {"query": ""}}, "filter": []}},
               "aggs": {
                   "fundingOrganization": {"terms": {"field": "fundingOrganization.whole_name", "size": 10}},
                   "recipientOrganization": {"terms": {"field": "recipientOrganization.whole_name", "size": 10}},
                   "awardPercentiles" : {"percentiles" : {"field" : "amountAwarded", "percents" : [0, 15, 30, 45, 60, 75, 90, 100]}}}}
SIZE = 10


def get_pagination(request, context, page):
    total_pages = math.ceil(context['results']['hits']['total'] / SIZE)
    if page < total_pages:
        context['next_page'] = request.path + '?' + urlencode({"json_query": context['json_query'], 'page': page + 1})
    if page != 1 and total_pages > 1:
        context['prev_page'] = request.path + '?' + urlencode({"json_query": context['json_query'], 'page': page - 1})


def get_terms_facet_size(request, context, json_query, page):
    json_query = copy.deepcopy(json_query)
    see_more_url = {}
    try:
        aggs = json_query["aggs"]
    except KeyError:
        aggs = BASIC_QUERY['aggs']
    for agg_name, agg in aggs.items():
        new_aggs = copy.deepcopy(aggs)
        if "terms" not in agg:
            continue
        size = agg["terms"]["size"]
        if size == 10:
            new_size = 50
            see_more_url[agg_name] = {"more": True}
        else:
            new_size = 10
            see_more_url[agg_name] = {"more": False}
        new_aggs[agg_name]["terms"]["size"] = new_size

        json_query["aggs"] = new_aggs
        see_more_url[agg_name]["url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query), 'page': page}) + '#' + agg_name

    context['see_more_url'] = see_more_url


def create_amount_aggregate(json_query):
    def round_amount(amount, round_up=True):
        round_func = math.ceil if round_up else math.floor
        if amount > 10000:
            return int(round_func(amount / 1000.0)) * 1000
        else:
            return int(round_func(amount / 100.0)) * 100

    amount_json_query = copy.deepcopy(json_query)

    es = get_es()
    results = es.search(body=amount_json_query, index=settings.ES_INDEX)

    values = results["aggregations"]["awardPercentiles"]["values"]
    range_list = [(values['0.0'], values['15.0']),
                  (values['15.0'], values['30.0']),
                  (values['30.0'], values['45.0']),
                  (values['45.0'], values['60.0']),
                  (values['60.0'], values['75.0']),
                  (values['75.0'], values['90.0']),
                  (values['90.0'], values['100.0'])]

    to_from_list = []
    for num, (from_, to_) in enumerate(range_list):
        if from_ == "NaN" or to_ == "NaN":
            break
        if num == 0:
            rounded_from = round_amount(from_, round_up=False)
        else:
            rounded_from = round_amount(from_)
        rounded_to = round_amount(to_)
        if rounded_from != rounded_to:
            to_from_list.append({"from": rounded_from, "to": rounded_to})
    if not to_from_list:
        if 'NaN' not in (values['0.0'], values['0.0']):
            to_from_list.append({"from": values['0.0'], "to": values['100.0']})
        else:
            #just some values here so as not to break anything
            to_from_list.append({"from": 0, "to": 0})

    json_query["aggs"]["amountAwarded"] = {"range": {"field": "amountAwarded", "ranges": to_from_list}}

    fixed_to_from_list = [
        {"from": 0, "to": 500},
        {"from": 500, "to": 1000},
        {"from": 1000, "to": 5000},
        {"from": 5000, "to": 10000},
        {"from": 10000, "to": 50000},
        {"from": 50000, "to": 100000},
        {"from": 100000, "to": 500000},
        {"from": 1000000, "to": 10000000},
        {"from": 10000000}
    ] 

    json_query["aggs"]["amountAwardedFixed"] = {"range": {"field": "amountAwarded", "ranges": fixed_to_from_list}}


def get_amount_facet_fixed(request, context, json_query):
    json_query = copy.deepcopy(json_query)
    try:
        current_filter = json_query["query"]["bool"]["filter"]
    except KeyError:
        current_filter = []
        json_query["query"]["bool"]["filter"] = current_filter
    new_filter = copy.deepcopy(current_filter)
    for filter in new_filter:
        if "range" in filter and "amountAwarded" in filter["range"]:
            range = filter["range"]["amountAwarded"]
            context["amount_range"] = {"from": range["gte"], "to": range["lt"]}
            filter.pop("range")
            json_query["query"]["bool"]["filter"] = new_filter
            context["results"]["aggregations"]["amountAwardedFixed"]["clear_url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})

    for bucket in context["results"]["aggregations"]["amountAwardedFixed"]['buckets']:
        new_filter = copy.deepcopy(current_filter)
        new_range = {"gte": bucket["from"]}
        to_ = bucket.get("to")
        if to_:
            new_range["lt"] = to_

        for filter in new_filter:
            # update if there is an existing amountAwarded filter
            if "range" in filter and "amountAwarded" in filter["range"]:
                filter["range"]["amountAwarded"] = new_range
                break
        else:
            # add one if there is not.
            new_filter.append({"range": {"amountAwarded": new_range}})
        json_query["query"]["bool"]["filter"] = new_filter
        bucket["url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})


def get_amount_facet(request, context, json_query):
    json_query = copy.deepcopy(json_query)
    try:
        current_filter = json_query["query"]["bool"]["filter"]
    except KeyError:
        current_filter = []
        json_query["query"]["bool"]["filter"] = current_filter

    ## get current amount to put in context for frontend
    new_filter = copy.deepcopy(current_filter)
    for filter in new_filter:
        if "range" in filter and "amountAwarded" in filter["range"]:
            range = filter["range"]["amountAwarded"]
            context["amount_range"] = {"from": range["gte"], "to": range["lt"]}
            filter.pop("range")
            json_query["query"]["bool"]["filter"] = new_filter
            context["results"]["aggregations"]["amountAwarded"]["clear_url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})

    for bucket in context["results"]["aggregations"]["amountAwarded"]['buckets']:
        new_filter = copy.deepcopy(current_filter)
        for filter in new_filter:
            # update if there is an existing amountAwarded filter
            if "range" in filter and "amountAwarded" in filter["range"]:
                filter["range"]["amountAwarded"] = {"gte": bucket["from"], "lt": bucket["to"]}
                break
        else:
            # add one if there is not.
            new_filter.append({"range": {"amountAwarded": {"gte": bucket["from"], "lt": bucket["to"]}}})
        json_query["query"]["bool"]["filter"] = new_filter
        bucket["url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})

def get_terms_facets(request, context, json_query):
    json_query = copy.deepcopy(json_query)
    try:
        current_filter = json_query["query"]["bool"]["filter"]
    except KeyError:
        current_filter = []
        json_query["query"]["bool"]["filter"] = current_filter

    if current_filter:
        json_query["query"]["bool"]["filter"] = []
        context["results"]["clear_all_facet_url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})

    aggregate_to_field = {agg_name: agg["terms"]["field"] for agg_name, agg in json_query["aggs"].items() if "terms" in agg}

    for aggregation, result in context["results"]["aggregations"].items():
        field_name = aggregate_to_field.get(aggregation)
        if not field_name:
            continue
        for bucket in result['buckets']:
            facet_value = bucket['key']
            new_filter_terms = collections.defaultdict(list)
            new_filter = []
            for filter in current_filter:
                if "term" in filter:
                    field, value = filter["term"].copy().popitem()
                    new_filter_terms[field].append(value)
                else:
                    new_filter.append(filter)

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
            for field, values in new_filter_terms.items():
                new_filter.extend({"term": {field: value}} for value in values)
            json_query["query"]["bool"]["filter"] = new_filter
            bucket["url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})
        if current_filter:
            filter_terms = collections.defaultdict(list)
            for filter in current_filter:
                if "term" in filter:
                    field, value = filter["term"].copy().popitem()
                    filter_terms[field].append(value)
            if field_name in filter_terms:
                new_filter = [filter for filter in current_filter if "term" not in filter]
                for field, values in filter_terms.items():
                    new_filter.extend({"term": {field: value}} for value in values if field != field_name)
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

        try:
            context['text_query'] = json_query["query"]["bool"]["must"]["query_string"]["query"]
        except KeyError:
            json_query = copy.deepcopy(BASIC_QUERY)
            json_query["query"]["bool"]["must"]["query_string"]["query"] = text_query
        if context['text_query'] == '*':
            context['text_query'] = ''

        try:
            create_amount_aggregate(json_query)
            results = es.search(body=json_query, size=SIZE, from_=(page - 1) * SIZE, index=settings.ES_INDEX)
        except elasticsearch.exceptions.RequestError as e:
            if e.error == 'search_phase_execution_exception':
                context['search_error'] = True
                return render(request, "search.html", context=context)
            raise

        for hit in results['hits']['hits']:
            hit['source'] = hit['_source']
        context['results'] = results
        context['json_query'] = json.dumps(json_query)
        get_terms_facets(request, context, json_query)
        get_amount_facet(request, context, json_query)
        get_amount_facet_fixed(request, context, json_query)
        get_terms_facet_size(request, context, json_query, page)
        get_pagination(request, context, page)

    return render(request, "search.html", context=context)


def flatten_mapping(mapping, current_path=''):
    for key, value in mapping.items():
        sub_properties = value.get('properties')
        if sub_properties:
            yield from flatten_mapping(sub_properties, current_path + "." + key)
        else:
            yield (current_path + "." + key).lstrip(".")


def flatten_schema(schema, path=''):
    for field, property in schema['properties'].items():
        if property['type'] == 'array':
            if property['items']['type'] == 'object':
                yield from flatten_schema(property['items'], path + '.' + field)
            else:
                yield (path + '.' + field).lstrip('.')
        if property['type'] == 'object':
            yield from flatten_schema(property, path + '/' + field)
        else:
            yield (path + '.' + field).lstrip('.')


def stats(request):
    text_query = request.GET.get('text_query')
    if not text_query:
        text_query = '*'
    context = {'text_query': text_query or ''}

    es = get_es()
    mapping = es.indices.get_mapping(index=settings.ES_INDEX)
    all_fields = list(flatten_mapping(mapping[settings.ES_INDEX]['mappings']['grant']['properties']))

    query = {"query": {"bool": {"must":
                {"query_string": {"query": text_query}}, "filter": {}}},
             "aggs": {}}

    schema = jsonref.load_uri(settings.GRANT_SCHEMA)
    schema_fields = set(flatten_schema(schema))

    for field in all_fields:
        query["aggs"][field + ":terms"] = {"terms": {"field": field, "size": 5}}
        query["aggs"][field + ":missing"] = {"missing": {"field": field}}
        query["aggs"][field + ":cardinality"] = {"cardinality": {"field": field}}

    if context['text_query'] == '*':
        context['text_query'] = ''

    field_info = collections.defaultdict(dict)
    results = es.search(body=query, index=settings.ES_INDEX, size=0)
    for field, aggregation in results['aggregations'].items():
        field_name, agg_type = field.split(':')
        field_info[field_name]["in_schema"] = field_name in schema_fields
        if agg_type == 'terms':
            field_info[field_name]["terms"] = aggregation["buckets"]
        if agg_type == 'missing':
            field_info[field_name]["found"] = results['hits']['total'] - aggregation["doc_count"]
        if agg_type == 'cardinality':
            field_info[field_name]["distinct"] = aggregation["value"]

    context['field_info'] = sorted(field_info.items(), key=lambda val: -val[1]["found"])
    context['results'] = results
    return render(request, "stats.html", context=context)
