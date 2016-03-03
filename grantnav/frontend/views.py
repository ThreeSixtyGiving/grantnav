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

BASIC_FILTER = [
    {"bool": {"should": []}},  # Funding Orgs
    {"bool": {"should": []}},  # Recipient Orgs
    {"bool": {"should": []}},  # Amount Awarded Fixed
    {"bool": {"should": []}},  # Amount Awarded
    {"bool": {"should": []}}   # Award Year
]

TERM_FILTERS = {
    "fundingOrganization": 0,
    "recipientOrganization": 1
}


BASIC_QUERY = {"query": {"bool": {"must":
                  {"query_string": {"query": ""}}, "filter": BASIC_FILTER}},
               "aggs": {
                   "fundingOrganization": {"terms": {"field": "fundingOrganization.whole_name", "size": 10}},
                   "recipientOrganization": {"terms": {"field": "recipientOrganization.whole_name", "size": 10}}}}
SIZE = 10

FIXED_AMOUNT_RANGES = [
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

FIXED_DATE_RANGES = [
    {"from": "now/y", "to": "now"},
    {"from": "now-1y/y", "to": "now/y"},
    {"from": "now-2y/y", "to": "now-1y/y"},
    {"from": "now-3y/y", "to": "now-2y/y"},
    {"from": "now-4y/y", "to": "now-3y/y"},
    {"from": "now-5y/y", "to": "now-4y/y"},
    {"from": "now-6y/y", "to": "now-5y/y"},
    {"from": "now-7y/y", "to": "now-6y/y"},
    {"from": "now-8y/y", "to": "now-7y/y"},
    {"from": "now-9y/y", "to": "now-8y/y"},
    {"from": "now-10y/y", "to": "now-9y/y"},
    {"from": "now-11y/y", "to": "now-10y/y"},
    {"from": "now-12y/y", "to": "now-11y/y"},
]


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
    amount_json_query["aggs"]["awardPercentiles"] = {"percentiles": {"field": "amountAwarded", "percents": [0, 15, 30, 45, 60, 75, 90, 100]}}

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

    json_query["aggs"]["amountAwardedFixed"] = {"range": {"field": "amountAwarded", "ranges": FIXED_AMOUNT_RANGES}}


def get_amount_facet_fixed(request, context, json_query):
    json_query = copy.deepcopy(json_query)
    json_query["aggs"]["amountAwardedFixed"] = {"range": {"field": "amountAwarded", "ranges": FIXED_AMOUNT_RANGES}}
    try:
        current_filter = json_query["query"]["bool"]["filter"][2]["bool"]["should"]
    except KeyError:
        json_query["query"]["bool"]["filter"] = copy.deepcopy(BASIC_FILTER)
        current_filter = json_query["query"]["bool"]["filter"][2]["bool"]["should"]

    main_results = context["results"]
    if current_filter:
        json_query["query"]["bool"]["filter"][2]["bool"]["should"] = []
        es = get_es()
        results = es.search(body=json_query, index=settings.ES_INDEX)
    else:
        results = context["results"]

    new_filter = copy.deepcopy(current_filter)
    if new_filter:
        range = new_filter[0]["range"]["amountAwarded"]
        context["amount_range_fixed"] = {"from": range["gte"], "to": range["lt"]}
        json_query["query"]["bool"]["filter"][2]["bool"]["should"] = []
        results["aggregations"]["amountAwardedFixed"]["clear_url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})

    for bucket in results["aggregations"]["amountAwardedFixed"]['buckets']:
        new_filter = []
        new_range = {"gte": bucket["from"]}
        to_ = bucket.get("to")
        if to_:
            new_range["lt"] = to_
        for filter in current_filter:
            if filter["range"]["amountAwarded"] == new_range:
                bucket["selected"] = True
            else:
                new_filter.append(filter)
        if not bucket.get("selected"):
            new_filter.append({"range": {"amountAwarded": new_range}})

        json_query["query"]["bool"]["filter"][2]["bool"]["should"] = new_filter
        bucket["url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})
    main_results["aggregations"]["amountAwardedFixed"] = results["aggregations"]["amountAwardedFixed"]


def get_amount_facet(request, context, json_query):
    json_query = copy.deepcopy(json_query)
    try:
        current_filter = json_query["query"]["bool"]["filter"][3]["bool"]["should"]
    except KeyError:
        json_query["query"]["bool"]["filter"] = copy.deepcopy(BASIC_FILTER)
        current_filter = json_query["query"]["bool"]["filter"][3]["bool"]["should"]

    ## get current amount to put in context for frontend
    new_filter = copy.deepcopy(current_filter)
    if new_filter:
        range = new_filter[0]["range"]["amountAwarded"]
        context["amount_range"] = {"from": range["gte"], "to": range["lt"]}
        json_query["query"]["bool"]["filter"][3]["bool"]["should"] = []
        context["results"]["aggregations"]["amountAwarded"]["clear_url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})

    for bucket in context["results"]["aggregations"]["amountAwarded"]['buckets']:
        new_filter = copy.deepcopy(current_filter)
        new_range = {"gte": bucket["from"]}
        to_ = bucket.get("to")
        if to_:
            new_range["lt"] = to_
        new_filter = [{"range": {"amountAwarded": new_range}}]
        json_query["query"]["bool"]["filter"][3]["bool"]["should"] = new_filter
        bucket["url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})


def create_date_aggregate(json_query):
    json_query["aggs"]["awardYear"] = {"date_range": {"field": "awardDate", "format": "yyyy", "ranges": FIXED_DATE_RANGES}}


def get_date_facets(request, context, json_query):
    json_query = copy.deepcopy(json_query)
    try:
        current_filter = json_query["query"]["bool"]["filter"][4]["bool"]["should"]
    except KeyError:
        json_query["query"]["bool"]["filter"] = copy.deepcopy(BASIC_FILTER)
        current_filter = json_query["query"]["bool"]["filter"][4]["bool"]["should"]
    main_results = context["results"]
    if current_filter:
        json_query["query"]["bool"]["filter"][4]["bool"]["should"] = []
        create_date_aggregate(json_query)
        es = get_es()
        results = es.search(body=json_query, index=settings.ES_INDEX)
    else:
        results = context["results"]

    for bucket in results['aggregations']['awardYear']['buckets']:
        range = {'format': 'year'}
        from_ = bucket.get("from_as_string")
        if from_:
            range["gte"] = from_
        to_ = bucket.get("to_as_string")
        if to_:
            range["le"] = to_

        filter_values = [filter["range"]['awardDate'] for filter in current_filter]

        if range in filter_values:
            bucket["selected"] = True
            range['format'] = 'year'
            filter_values.remove(range)
        else:
            range['format'] = 'year'
            filter_values.append(range)

        new_filter = [{"range": {"awardDate": value}} for value in filter_values]
        json_query["query"]["bool"]["filter"][4]["bool"]["should"] = new_filter
        bucket["url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})
    if current_filter:
        json_query["query"]["bool"]["filter"][4]["bool"]["should"] = []
        results['aggregations']["awardYear"]['clear_url'] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})
    main_results['aggregations']["awardYear"] = results['aggregations']["awardYear"]


def get_terms_facets(request, context, json_query, field, aggregate, bool_index):
    json_query = copy.deepcopy(json_query)
    try:
        current_filter = json_query["query"]["bool"]["filter"][bool_index]["bool"]["should"]
    except KeyError:
        json_query["query"]["bool"]["filter"] = copy.deepcopy(BASIC_FILTER)
        current_filter = json_query["query"]["bool"]["filter"][bool_index]["bool"]["should"]

    main_results = context["results"]
    if current_filter:
        json_query["query"]["bool"]["filter"][bool_index]["bool"]["should"] = []
        es = get_es()
        results = es.search(body=json_query, index=settings.ES_INDEX)
    else:
        results = context["results"]

    for bucket in results['aggregations'][aggregate]['buckets']:
        facet_value = bucket['key']
        filter_values = [filter["term"][field] for filter in current_filter]
        if facet_value in filter_values:
            bucket["selected"] = True
            filter_values.remove(facet_value)
        else:
            filter_values.append(facet_value)

        new_filter = [{"term": {field: value}} for value in filter_values]
        json_query["query"]["bool"]["filter"][bool_index]["bool"]["should"] = new_filter
        bucket["url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})
    if current_filter:
        json_query["query"]["bool"]["filter"][bool_index]["bool"]["should"] = []
        results['aggregations'][aggregate]['clear_url'] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})
    main_results['aggregations'][aggregate] = results['aggregations'][aggregate]


def get_clear_all(request, context, json_query):
    json_query = copy.deepcopy(json_query)
    try:
        current_filter = json_query["query"]["bool"]["filter"]
    except KeyError:
        json_query["query"]["bool"]["filter"] = copy.deepcopy(BASIC_FILTER)
        current_filter = json_query["query"]["bool"]["filter"]
        
    if current_filter != BASIC_FILTER:
        json_query["query"]["bool"]["filter"] = copy.deepcopy(BASIC_FILTER)
        context["results"]["clear_all_facet_url"] = request.path + '?' + urlencode({"json_query": json.dumps(json_query)})


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
            create_date_aggregate(json_query)
            results = es.search(body=json_query, size=SIZE, from_=(page - 1) * SIZE, index=settings.ES_INDEX)
            json_query["aggs"].pop("awardYear")
            json_query["aggs"].pop("amountAwarded")
            json_query["aggs"].pop("amountAwardedFixed")
        except elasticsearch.exceptions.RequestError as e:
            if e.error == 'search_phase_execution_exception':
                context['search_error'] = True
                return render(request, "search.html", context=context)
            raise

        for hit in results['hits']['hits']:
            hit['source'] = hit['_source']
        context['results'] = results
        context['json_query'] = json.dumps(json_query)

        get_clear_all(request, context, json_query)
        for filter_name, index in TERM_FILTERS.items():
            get_terms_facets(request, context, json_query, filter_name + ".whole_name", filter_name, index)

        get_amount_facet(request, context, json_query)
        get_amount_facet_fixed(request, context, json_query)
        get_date_facets(request, context, json_query)
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


def grant(request, grant_id):
    query = {"query": {"bool": {"filter":
                [{"term": {"id": grant_id}}]
    }}}
    es = get_es()
    results = es.search(body=query, index=settings.ES_INDEX, size=1)
    assert results['hits']['total'] == 1
    context = {}
    context['grant'] = results['hits']['hits'][0]
    context['grant']['source'] = context['grant']['_source']
    return render(request, "grant.html", context=context)
