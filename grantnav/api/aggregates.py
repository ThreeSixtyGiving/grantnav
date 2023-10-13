import json
import warnings

from django.views import View
from django.http import JsonResponse
from grantnav.frontend.views import search, filter_search_ajax


class Search(View):
    def get(self, *args, **kwargs):
        # Append .aggregates_api as this is the flag we currently switch on in the
        # main search functions to know what format we will return results as.
        self.request.path = self.request.path + ".aggregates_api"
        context = search(self.request)

        # Don't send actual grant documents back. This is a quirk of re-using
        # the GrantNav code path for the query. Remove these fields:
        # - Ease of testing due to unique index specific document "_id" fields being exposed.
        # - This makes the json response smaller
        for currency in context["results"]["aggregations"]["currency_stats"]["buckets"]:
            del currency["smallest_grant"]
            del currency["largest_grant"]

        del context["results"]["aggregations"]["earliest_grant"]
        del context["results"]["aggregations"]["latest_grant"]

        ret = {
            "aggregations": context["results"]["aggregations"],
            "hits": context["results"]["hits"],
        }

        # Add in some additional aggregate fields that are returned by
        # separate requests.

        # [ (parentField, childField), ]
        for data_field in [
            ("fundingOrganization", "id_and_name"),
            ("grantProgramme", "title_keyword"),
            ("additional_data", "recipientDistrictName"),
        ]:
            try:
                results = filter_search_ajax(
                    self.request, data_field[0], data_field[1]
                )["aggregations"][data_field[0]]

                # This field is a json array field ["org id, "org name"]
                if data_field[1] == "id_and_name":
                    new_results = []
                    for bucket in results["buckets"]:
                        name_id = json.loads(bucket["key"])
                        new_results.append(
                            {
                                "key": name_id[1],
                                "name": name_id[0],
                                "doc_count": bucket["doc_count"],
                                "url": bucket["url"],
                                "selected": bucket.get("selected", False),
                            }
                        )
                    ret["aggregations"][data_field[0]]["buckets"] = new_results

                else:
                    ret["aggregations"][data_field[0]] = results

            # There is a possibility that the data can't support the generated id_and_name field
            except KeyError as e:
                warnings.warn(str(e))
                continue

        return JsonResponse(ret)
