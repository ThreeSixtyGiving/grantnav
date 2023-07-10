
from django.views import View
from django.http import JsonResponse
from grantnav.frontend.views import search


class Search(View):
    def get(self, *args, **kwargs):
        # Append .insights_api as this is the value we currently switch on in the
        # main search function
        self.request.path = self.request.path + ".insights_api"
        context = search(self.request)

        ret = {
            "aggregations": context["results"]["aggregations"],
            "hits" : context["results"]["hits"],
        }

        return JsonResponse(ret)



