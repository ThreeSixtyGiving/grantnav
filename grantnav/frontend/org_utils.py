
def new_stats_by_currency(org_result):
    """ Takes a org dict and creates a sorted and ease of use in templates list"""
    stats_by_currency = []

    for currency, stat in org_result["aggregate"]["currencies"].items():
        stat["currency"] = currency
        stats_by_currency.append(stat)

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
    org_ids = [org_result["id"]]

    if org_result["ftcData"]:
        org_ids.extend(org_result["ftcData"]["orgIDs"])

    return list(set(org_ids))
