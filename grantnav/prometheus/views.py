import re
import os

from django.conf import settings
from django.http.response import HttpResponse
from django.views import View
from prometheus_client import Gauge
from prometheus_client.exposition import generate_latest
from grantnav.index import get_index

from grantnav.frontend.views import totals_query

NUM_ERRORS_LOGGED = Gauge(
    "total_import_errors_logged", "Total number of errors logged by last import"
)

TOTAL_GRANTS = Gauge(
    "total_grants", "Total number of grants in the system"
)


class ServiceMetrics(View):
    def _num_errors_log(self):
        errors = 0

        log_dir = getattr(settings, "GRANTNAV_LOG_DIR")
        index = get_index()

        search_term = re.compile("failure|failed|exception|error", re.IGNORECASE)

        log_file = os.path.join(log_dir, "load_%s.log" % index)

        try:
            with open(log_file, "r") as lf:
                log = lf.read()
                errors = len(search_term.findall(log))
        except FileNotFoundError:
            errors = -1
            pass

        NUM_ERRORS_LOGGED.set(errors)

    def _total_grants(self):
        results = totals_query()

        TOTAL_GRANTS.set(results['hits']['total']['value'])

    def get(self, *args, **kwargs):
        # Update gauges
        self._num_errors_log()
        self._total_grants()
        # Generate latest uses default of the global registry
        return HttpResponse(generate_latest(), content_type="text/plain")
