import collections
import copy
import json

import elasticsearch.exceptions
from django.utils.http import urlencode
from django.shortcuts import render, redirect
from grantnav.frontend.org_utils import new_ordered_names, new_org_ids, new_stats_by_currency

from grantnav.frontend.search_helpers import get_results, get_request_type_and_size, get_terms_facets, SIZE
import grantnav.frontend.search_helpers as helpers

BASIC_FILTER = [
    {"bool": {"should": []}},  # currency
]

TermFacet = collections.namedtuple("TermFacet", "field_name param_name filter_index display_name is_json facet_size")

TERM_FACETS = [TermFacet("currency", "currency", 0, "Currency", False, 5000)]


BASIC_QUERY = {
    "query": {"bool": {"must": {"query_string": {"query": "", "default_field": "*"}}, "filter": BASIC_FILTER}},
    "sort": {"_score": {"order": "desc"}},
    "aggs": {},
}

for term_facet in TERM_FACETS:
    BASIC_QUERY["aggs"][term_facet.param_name] = {
        "terms": {"field": term_facet.field_name, "size": term_facet.facet_size}
    }


def get_dropdown_filters(context):
    context["dropdownFilterOptions"] = []
    context["dropdownFilterOptions"].append({"value": "_score desc", "label": "Best Match"})
    context["dropdownFilterOptions"].append({"value": "grants desc", "label": "Grant Count - Highest First"})
    context["dropdownFilterOptions"].append({"value": "currencyTotal.GBP desc", "label": "Total GBP Amount - Highest First"})
    context["dropdownFilterOptions"].append({"value": "currencyTotal.GBP asc", "label": "Total GBP Amount - Lowest First"})
    context["dropdownFilterOptions"].append({"value": "currencyAvgAmount.GBP desc", "label": "Average GBP Grant Amount - Highest First"})
    context["dropdownFilterOptions"].append({"value": "currencyAvgAmount.GBP asc", "label": "Average GBP Grant Amount - Lowest First"})


def create_json_query_from_parameters(request):
    """Transforms the URL GET parameters of the request into an object (json_query) that is to be used by elasticsearch"""

    json_query = copy.deepcopy(BASIC_QUERY)
    json_query["query"]["bool"]["must"]["query_string"]["query"] = request.GET.get("query", "*")
    json_query["query"]["bool"]["must"]["query_string"]["default_field"] = request.GET.get("default_field", "*")

    sort_order = request.GET.get("sort", "").split()
    if sort_order and len(sort_order) == 2:
        sort = {sort_order[0]: {"order": sort_order[1]}}
        json_query["sort"] = sort

    for term_facet in TERM_FACETS:
        helpers.term_facet_from_parameters(
            request,
            json_query,
            term_facet.field_name,
            term_facet.param_name,
            term_facet.filter_index,
            term_facet.display_name,
            term_facet.is_json,
            data_type="funder"
        )

    return json_query


def create_parameters_from_json_query(json_query, **extra_parameters):
    """Transforms json_query (the query that is passed to elasticsearch) to URL GET parameters"""

    parameters = {}

    must_query = json_query["query"]["bool"]["must"]

    # For the funder/recipient filter ajax request a new must clause is added here making this a list not a dict.
    # would be better for it to be a list always but will be difficult for backwards compatibility currently.
    if isinstance(must_query, list):
        # second search terms should not go in paremeters.
        must_query = must_query[0]

    parameters["query"] = [must_query["query_string"]["query"]]
    parameters["default_field"] = [must_query["query_string"]["default_field"]]

    sort_key = list(json_query["sort"].keys())[0]
    parameters["sort"] = [sort_key + " " + json_query["sort"][sort_key]["order"]]

    for term_facet in TERM_FACETS:
        helpers.term_parameters_from_json_query(
            parameters,
            json_query,
            term_facet.field_name,
            term_facet.param_name,
            term_facet.filter_index,
            term_facet.display_name,
            term_facet.is_json,
        )

    parameter_list = []

    for parameter, list_value in parameters.items():
        for value in list_value:
            parameter_list.append((parameter, value))
    for parameter, value in extra_parameters.items():
        parameter_list.append((parameter, value))

    return urlencode(parameter_list)


def search(request):
    [result_format, results_size] = get_request_type_and_size(request)

    context = {}

    json_query = create_json_query_from_parameters(request)

    default_field = request.GET.get("default_field")

    # same as grants search consider refactoring.
    text_query = request.GET.get("text_query")
    if text_query is not None:
        if not text_query:
            text_query = "*"
        try:
            json_query["query"]["bool"]["must"]["query_string"]["query"] = text_query
        except KeyError:
            json_query = copy.deepcopy(BASIC_QUERY)
            json_query["query"]["bool"]["must"]["query_string"]["query"] = text_query

        if default_field:
            json_query["query"]["bool"]["must"]["query_string"]["default_field"] = default_field
        return redirect(request.path + "?" + create_parameters_from_json_query(json_query))

    sort_order = request.GET.get("sort", "").split()
    if sort_order and len(sort_order) == 2:
        new_sort = {sort_order[0]: {"order": sort_order[1]}}
        old_sort = json_query["sort"]
        if new_sort != old_sort:
            json_query["sort"] = new_sort
            return redirect(request.path + "?" + create_parameters_from_json_query(json_query))

    results = None
    if json_query:
        try:
            page = int(request.GET.get("page", 1))
            if page < 1:
                page = 1
        except ValueError:
            page = 1

        try:
            context["text_query"] = json_query["query"]["bool"]["must"]["query_string"]["query"]
            default_field = json_query["query"]["bool"]["must"]["query_string"]["default_field"]
        except KeyError:
            json_query = copy.deepcopy(BASIC_QUERY)
            json_query["query"]["bool"]["must"]["query_string"]["query"] = ""
            context["text_query"] = ""
            if default_field:
                json_query["query"]["bool"]["must"]["query_string"]["default_field"] = default_field
            default_field = json_query["query"]["bool"]["must"]["query_string"]["default_field"]
        # same as grant ends

        if context["text_query"] == "*":
            context["text_query"] = ""

        try:
            results = get_results(json_query, results_size, (page - 1) * SIZE, data_type="funder")
        except elasticsearch.exceptions.RequestError as e:
            if e.error == "search_phase_execution_exception":
                context["search_error"] = True
                return render(request, "search_funders.html", context=context)
            raise

        for hit in results["hits"]["hits"]:
            hit["source"] = hit["_source"]
            hit["stats_by_currency"] = new_stats_by_currency(hit["source"])

            org_ids = new_org_ids(hit["source"])

            parameters = [("fundingOrganization", org_id) for org_id in org_ids]

            hit["grant_search_parameters"] = urlencode(parameters)

            names = new_ordered_names(hit["source"])

            hit["org_ids"] = org_ids
            hit["names"] = names
            hit["other_names"] = names[1:]

        context["results"] = results
        context["json_query"] = json.dumps(json_query)
        context["query"] = json_query

        context["selected_facets"] = collections.defaultdict(list)
        helpers.get_clear_all(request, context, json_query, BASIC_FILTER, create_parameters_from_json_query)

        for term_facet in TERM_FACETS:
            get_terms_facets(
                request,
                context,
                json_query,
                term_facet.field_name,
                term_facet.param_name,
                term_facet.filter_index,
                term_facet.display_name,
                BASIC_FILTER,
                create_parameters_from_json_query,
                term_facet.is_json,
                data_type='funder'
            )

        helpers.get_pagination(request, context, page, create_parameters_from_json_query)

        context["selected_facets"] = dict(context["selected_facets"])

        get_dropdown_filters(context)

        return render(request, "search_funders.html", context=context)
