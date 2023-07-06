
from django.views import View
from django.http import JsonResponse
from grantnav.frontend.views import search


class Search(View):
    def get(self, *args, **kwargs):
        return search(self.request)
        #return JsonResponse(data)



