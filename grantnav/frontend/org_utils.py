from grantnav.frontend.search_helpers import get_results


def new_stats_by_currency(org_result):
    """ Takes a org dict and creates a sorted list of currencies for ease of use in templates"""
    stats_by_currency = []

    for recipient_type in ["recipient_org", "recipient_ind"]:
        try:
            for currency, stat in org_result["aggregate"]["currencies"].items():
                stat["currency"] = currency
                # Copy the currency name for convenience in the list
                stat[recipient_type]["currency"] = currency
                stat[recipient_type]["recipient_type"] = recipient_type
                stats_by_currency.append(stat[recipient_type])
        except KeyError:
            continue

        # sort the list with the largest total amount currency first
        stats_by_currency.sort(key=lambda i: i["total"], reverse=True)

    return stats_by_currency


def new_ordered_names(org_result):
    # Name ordering is important: Publisher, FTC, Grant
    names = []

    if org_result["publisherName"] and org_result["publisherName"] not in names:
        names.append(org_result["publisherName"])

    if org_result["ftcData"] and org_result["ftcData"]["name"] not in names:
        names.append(org_result["ftcData"]["name"])

    if org_result["additionalData"]["alternative_names"]:
        names.extend(org_result["additionalData"]["alternative_names"])

    if org_result["name"] not in names:
        names.append(org_result["name"])

    if len(names) == 0:
        names = [org_result["id"]]

    return names


def new_org_ids(org_result):
    return [org_result["id"], *org_result.get("non_primary_org_ids", [])]


class OrgNotFoundError(Exception):
    pass


orgs_cache = {"funder": {}, "recipient": {}}


def get_org(org_id, org_type):
    """ org_type: recipient, funder
    returns an organisation match
    """
    # Don't allow the memory cache to grow infinitely
    if len(orgs_cache[org_type].keys()) > 300000:
        orgs_cache[org_type] = {}

    try:
        org = orgs_cache[org_type][org_id]
        return org
    except KeyError:
        pass

    query = {
        "query": {
            "bool": {
                "filter": [
                    {"term": {"orgIDs": org_id}}
                ]
            }
        }
    }

    try:
        org = get_results(query, data_type=org_type)["hits"]["hits"][0]["_source"]
        # Save the org to the cache
        orgs_cache[org_type][org_id] = org
        return org
    except (IndexError, KeyError):
        # Failed to find org
        raise OrgNotFoundError


def update_request_to_include_all_org_ids(request):
    """ If someone provides an org-id append all other known org-ids to the query
    This is done so that it doesn't matter which org-id of many for a certain org
    is provided we can still return the results.
    """
    do_redirect = False
    request_get_copy = request.GET.copy()

    for entity_type in [("fundingOrganization", "funder"), ("recipientOrganization", "recipient")]:
        # Match the supplied org-id to any other org-ids in use
        if org_ids := request.GET.getlist(entity_type[0]):
            for org_id in org_ids:
                try:
                    for additional_org_id in get_org(org_id, entity_type[1])["orgIDs"]:
                        if additional_org_id not in org_ids:
                            request_get_copy.appendlist(entity_type[0], additional_org_id)
                            do_redirect = True
                except OrgNotFoundError:
                    pass

    if do_redirect:
        return request.path + '?' + request_get_copy.urlencode()
