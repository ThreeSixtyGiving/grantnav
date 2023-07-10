import copy
import math
import re
import json

from django.conf import settings
from retry import retry

from grantnav.search import get_es
from grantnav.index import get_index

SIZE = 20


def clean_object(obj):
    for key, value in list(obj.items()):
        if isinstance(value, dict):
            clean_object(value)
        elif isinstance(value, list):
            clean_array(value)
        if isinstance(value, (dict, list)) and not value:
            obj.pop(key, None)


def clean_array(array):
    new_array = []
    for item in array:
        if isinstance(item, dict):
            clean_object(item)
        elif isinstance(item, list):
            clean_array(item)
        if isinstance(item, (dict, list, str)) and item:
            new_array.append(item)
    array[:] = new_array
    return array


def clean_for_es(json_query):
    clean_object(json_query)
    return json_query


@retry(tries=5, delay=0.5, backoff=2, max_delay=20)
def get_results(json_query, size=10, from_=0, data_type="grant"):
    es = get_es()
    extra_context = json_query.pop("extra_context", None)

    new_json_query = clean_for_es(copy.deepcopy(json_query))

    if "query" not in new_json_query:
        new_json_query["query"] = {}

    query = new_json_query["query"]

    if "bool" not in query:
        query["bool"] = {}

    if "filter" not in query["bool"]:
        query["bool"]["filter"] = []

    # takes query which only has a dict e.g.
    # query["bool"]["filter"]["term"]["additional_data.recipient..": "value"]
    # and turns it into a list of filters so that we can always append data_type
    if type(query["bool"]["filter"]) == dict:
        single_term_query = query["bool"]["filter"]
        query["bool"]["filter"] = [single_term_query]

    query["bool"]["filter"].append({"term": {"dataType": {"value": data_type}}})

    if from_ == -1:
        results = es.search(body=new_json_query, index=get_index(), track_total_hits=True)
    else:
        results = es.search(body=new_json_query, size=size, from_=from_, index=get_index(), track_total_hits=True)

    if extra_context is not None:
        json_query["extra_context"] = extra_context
    return results


def get_request_type_and_size(request):
    results_size = SIZE

    #  e.g. search.csv / search.json / search.widgets_api
    match = re.search(r"\.(\w+)$", request.path)
    if match and match.group(1) in ["csv", "json", "ajax", "widgets_api", "insights_api"]:
        result_format = match.group(1)
        results_size = settings.FLATTENED_DOWNLOAD_LIMIT
        if result_format == "insights_api":
            # We only want the aggregate data
            results_size = 0
    else:
        result_format = "html"

    return [result_format, results_size]


def get_data_from_path(path, data):
    current_pos = data
    for part in path.split("."):
        try:
            part = int(part)
        except ValueError:
            pass
        try:
            current_pos = current_pos[part]
        except (KeyError, IndexError, TypeError):
            return ""
    if isinstance(current_pos, list):
        return ", ".join([str(i) for i in current_pos])
    else:
        return current_pos


def get_pagination(request, context, page, create_parameters_from_json_query):
    total_pages = math.ceil(context["results"]["hits"]["total"]["value"] / SIZE)
    context["total_pages"] = total_pages
    context["pages"] = []
    if page != 1 and total_pages > 5:
        context["pages"].append(
            {
                "url": request.path + "?" + create_parameters_from_json_query(context["query"], page=1),
                "type": "first",
                "label": "First",
            }
        )

    if page != 1 and total_pages > 1:
        context["pages"].append(
            {
                "url": request.path + "?" + create_parameters_from_json_query(context["query"], page=page - 1),
                "type": "prev",
                "label": "Previous",
            }
        )

    if total_pages > 1 and page > 3:
        context["pages"].append({"type": "ellipsis"})

    if total_pages > 1 and page > 2:
        context["pages"].append(
            {
                "url": request.path + "?" + create_parameters_from_json_query(context["query"], page=page - 2),
                "type": "number",
                "label": str(page - 2),
            }
        )
    if total_pages > 1 and page > 1:
        context["pages"].append(
            {
                "url": request.path + "?" + create_parameters_from_json_query(context["query"], page=page - 1),
                "type": "number",
                "label": str(page - 1),
            }
        )

    context["pages"].append(
        {
            "url": request.path + "?" + create_parameters_from_json_query(context["query"], page=page),
            "type": "number",
            "label": str(page),
            "active": True,
        }
    )

    if page <= total_pages - 1:
        context["pages"].append(
            {
                "url": request.path + "?" + create_parameters_from_json_query(context["query"], page=page + 1),
                "type": "number",
                "label": str(page + 1),
            }
        )
    if page <= total_pages - 2:
        context["pages"].append(
            {
                "url": request.path + "?" + create_parameters_from_json_query(context["query"], page=page + 2),
                "type": "number",
                "label": str(page + 2),
            }
        )

    if page <= total_pages - 3:
        context["pages"].append({"type": "ellipsis"})

    if page < total_pages:
        context["pages"].append(
            {
                "url": request.path + "?" + create_parameters_from_json_query(context["query"], page=page + 1),
                "type": "next",
                "label": "Next",
            }
        )

    if page < total_pages and total_pages > 5:
        context["pages"].append(
            {
                "url": request.path + "?" + create_parameters_from_json_query(context["query"], page=total_pages),
                "type": "last",
                "label": "Last",
            }
        )


def get_clear_all(request, context, json_query, basic_filter, create_parameters_from_json_query):
    json_query = copy.deepcopy(json_query)
    try:
        current_filter = json_query["query"]["bool"]["filter"]
    except KeyError:
        json_query["query"]["bool"]["filter"] = copy.deepcopy(basic_filter)
        current_filter = json_query["query"]["bool"]["filter"]

    if current_filter != basic_filter:
        json_query["query"]["bool"]["filter"] = copy.deepcopy(basic_filter)
        context["results"]["clear_all_facet_url"] = request.path + "?" + create_parameters_from_json_query(json_query)


def get_terms_facets(
    request,
    context,
    json_query,
    field,
    aggregate,
    bool_index,
    display_name,
    basic_filter,
    create_parameters_from_json_query,
    is_json=False,
    path=None,
    data_type="grant"
):

    if not path:
        path = request.path

    json_query = copy.deepcopy(json_query)
    try:
        if "must_not" in json_query["query"]["bool"]["filter"][bool_index]["bool"]:
            bool_condition = "must_not"
        else:
            bool_condition = "should"

        current_filter = json_query["query"]["bool"]["filter"][bool_index]["bool"].get(bool_condition, [])
    except KeyError:
        json_query["query"]["bool"]["filter"] = copy.deepcopy()
        current_filter = json_query["query"]["bool"]["filter"][bool_index]["bool"].get(bool_condition, [])

    main_results = context["results"]
    if current_filter:
        json_query["query"]["bool"]["filter"][bool_index]["bool"][bool_condition] = []
        results = get_results(json_query, data_type=data_type)
    else:
        results = context["results"]

    if bool_condition == "must_not":
        display_name = "Excluded " + display_name

    for filter in current_filter:
        new_filter = [x for x in current_filter if x != filter]
        json_query["query"]["bool"]["filter"][bool_index]["bool"][bool_condition] = new_filter
        display_value = filter["term"][field]
        if is_json:
            display_value = json.loads(display_value)[0]
        context["selected_facets"][display_name].append(
            {
                "url": path + "?" + create_parameters_from_json_query(json_query),
                "display_value": display_value,
            }
        )

    for bucket in results["aggregations"][aggregate]["buckets"]:
        facet_value = bucket["key"]
        filter_values = [filter["term"][field] for filter in current_filter]
        if facet_value in filter_values:
            bucket["selected"] = True
            filter_values.remove(facet_value)
        else:
            filter_values.append(facet_value)

        new_filter = [{"term": {field: value}} for value in filter_values]
        json_query["query"]["bool"]["filter"][bool_index]["bool"][bool_condition] = new_filter
        bucket["url"] = path + "?" + create_parameters_from_json_query(json_query)
    if current_filter:
        json_query["query"]["bool"]["filter"][bool_index]["bool"][bool_condition] = []
        results["aggregations"][aggregate]["clear_url"] = path + "?" + create_parameters_from_json_query(json_query)
        results["aggregations"][aggregate]["exclude"] = True if bool_condition == "must_not" else False

    main_results["aggregations"][aggregate] = results["aggregations"][aggregate]


def term_facet_from_parameters(request, json_query, field_name, param_name, bool_index, field, is_json=False, data_type="grant"):
    new_filter = []

    if is_json:
        query_filter = []
        for value in request.GET.getlist(param_name):
            query_filter.append({"term": {param_name + '.id': value}})

        if query_filter:
            query = {
                "query": {
                    "bool": {"filter": [{"bool": {"should": query_filter}}]}
                },
                "aggs": {
                    param_name: {"terms": {"field": field_name, "size": len(query_filter)}}
                }
            }

            results = get_results(query, 1, data_type=data_type)

            for bucket in results['aggregations'][param_name]['buckets']:
                new_filter.append({"term": {field_name: bucket['key']}})

    else:
        for value in request.GET.getlist(param_name):
            new_filter.append({"term": {field_name: value}})

    if request.GET.get("exclude_" + param_name):
        json_query["query"]["bool"]["filter"][bool_index]["bool"].pop("should", None)
        json_query["query"]["bool"]["filter"][bool_index]["bool"]["must_not"] = new_filter
    else:
        json_query["query"]["bool"]["filter"][bool_index]["bool"]["should"] = new_filter


def term_parameters_from_json_query(parameters, json_query, field_name, param_name, bool_index, field, is_json=False):
    values = []
    if "must_not" in json_query["query"]["bool"]["filter"][bool_index]["bool"]:
        filters = json_query["query"]["bool"]["filter"][bool_index]["bool"]["must_not"]
        must_not = True
    else:
        filters = json_query["query"]["bool"]["filter"][bool_index]["bool"]["should"]
        must_not = False

    for filter in filters:
        if is_json:
            values.append(json.loads(filter['term'][field_name])[1])
        else:
            values.append(filter['term'][field_name])
    parameters[param_name] = values
    if must_not:
        parameters["exclude_" + param_name] = "true"
