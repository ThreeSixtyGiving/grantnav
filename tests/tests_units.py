import json
import time
import os

from django.test import TestCase, Client, RequestFactory, override_settings
from django.urls import reverse_lazy

from dataload.import_to_elasticsearch import import_to_elasticsearch
from grantnav.frontend.search_helpers import get_pagination
from grantnav.frontend.views import BASIC_QUERY, create_parameters_from_json_query


prefix = os.path.join(os.path.dirname(__file__), "data")


@override_settings(PROVENANCE_JSON=os.path.join(prefix, "data.json"))
class UnitTest(TestCase):
    """
    This setUpClass will be executed only once before all test methods in the class are executed.
    It's used to load data to Elasticsearch to avoid redundant loading for each test.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        import_to_elasticsearch(
            [
                os.path.join(prefix, "a002400000KeYdsAAF.json"),
                os.path.join(prefix, "grantnav-20180903134856.json"),
                os.path.join(prefix, "a002400000nO46WAAS.json"),
            ],
            clean=True,
            funders=os.path.join(prefix, "funders.jsonl"),
            recipients=os.path.join(prefix, "recipients.jsonl"),
        )
        time.sleep(2)  # Elasticsearch needs some time to commit its data

    def setUp(self):
        """
        This setUp method will be executed before each test method.
        """
        self.client = Client()

    def test_home(self):
        response = self.client.get("/")
        self.assertContains(response, "GrantNav")
        self.assertContains(response, "Search")
        self.assertContains(response, "GrantNav user guide")
        self.assertNotContains(response, "grant-making")

    def test_prometheus(self):
        response = self.client.get("/prometheus/metrics")
        self.assertContains(response, "total_grants 1254.0")

    def test_search_query(self):
        search_queries_and_expected_grants = [
            ("gardens+AND+fundingOrganization.id:GB-CHC-1156077", 7),
            ("E09000033+AND+fundingOrganization.id:GB-CHC-1156077", 19),
            ("E10000023+AND+fundingOrganization.id:GB-CHC-1156077", 0),
            ("Esmee", 5),
            ("Esmée", 5),
            ("Esmeé", 5),
        ]

        for search_query, expected_grants in search_queries_and_expected_grants:
            r = self.client.get(f"/search?text_query={search_query}", follow=True)
            self.assertEqual(
                r.context["results"]["hits"]["total"]["value"], expected_grants
            )

    def test_json_download(self):
        initial_response = self.client.get("/search.json?text_query=gardens")
        self.assertEqual(initial_response.status_code, 302)
        response = self.client.get(initial_response.url)
        json_string = b"".join(response.streaming_content).decode("utf-8")
        json.loads(json_string)

    def test_orgid_with_dots(self):
        org = self.client.get("/org/XI-GRID-grid.5292.c")
        self.assertEqual(org.status_code, 200)

    def test_districts_datatables(self):
        datatables = self.client.get(
            "/grants_datatables?draw=1&columns%5B0%5D%5Bdata%5D=title&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=amountAwarded&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=fundingOrganization.0.name&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=recipientOrganization.0.name&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=awardDate&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=description&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=desc&start=0&length=220&search%5Bvalue%5D=&search%5Bregex%5D=false&recipientDistrictName=Sir+Ddinbych+-+Denbighshire&_=1668523317785"
        )
        self.assertEqual(datatables.status_code, 200)

    def test_region_datatables(self):
        datatables = self.client.get(
            "/grants_datatables?draw=1&columns%5B0%5D%5Bdata%5D=title&columns%5B0%5D%5Bname%5D=&columns%5B0%5D%5Bsearchable%5D=true&columns%5B0%5D%5Borderable%5D=false&columns%5B0%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B0%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B1%5D%5Bdata%5D=amountAwarded&columns%5B1%5D%5Bname%5D=&columns%5B1%5D%5Bsearchable%5D=true&columns%5B1%5D%5Borderable%5D=true&columns%5B1%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B1%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B2%5D%5Bdata%5D=fundingOrganization.0.name&columns%5B2%5D%5Bname%5D=&columns%5B2%5D%5Bsearchable%5D=true&columns%5B2%5D%5Borderable%5D=true&columns%5B2%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B2%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B3%5D%5Bdata%5D=recipientOrganization.0.name&columns%5B3%5D%5Bname%5D=&columns%5B3%5D%5Bsearchable%5D=true&columns%5B3%5D%5Borderable%5D=true&columns%5B3%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B3%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B4%5D%5Bdata%5D=awardDate&columns%5B4%5D%5Bname%5D=&columns%5B4%5D%5Bsearchable%5D=true&columns%5B4%5D%5Borderable%5D=true&columns%5B4%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B4%5D%5Bsearch%5D%5Bregex%5D=false&columns%5B5%5D%5Bdata%5D=description&columns%5B5%5D%5Bname%5D=&columns%5B5%5D%5Bsearchable%5D=true&columns%5B5%5D%5Borderable%5D=true&columns%5B5%5D%5Bsearch%5D%5Bvalue%5D=&columns%5B5%5D%5Bsearch%5D%5Bregex%5D=false&order%5B0%5D%5Bcolumn%5D=0&order%5B0%5D%5Bdir%5D=desc&start=0&length=220&search%5Bvalue%5D=&search%5Bregex%5D=false&recipientRegionName=Wales&_=1668523901299"
        )
        self.assertEqual(datatables.status_code, 200)

    def test_old_org_to_new_redirects(self):
        self.assertEqual(self.client.get("/funder/GB-CHC-1126147").status_code, 302)
        self.assertEqual(self.client.get("/recipient/GB-COH-08523414").status_code, 302)
        self.assertEqual(self.client.get("/publisher/GB-CHC-1126147").status_code, 302)

    def test_datasets_page(self):
        self.assertEqual(self.client.get("/datasets/").status_code, 200)

    def test_get_pagination_single_page(self):
        request = RequestFactory().get("/")
        context = {"results": {"hits": {"total": {"value": 5}}}, "query": BASIC_QUERY}
        get_pagination(request, context, 1, create_parameters_from_json_query)
        self.assertEqual(len(context["pages"]), 1)

        page = context["pages"].pop(0)
        self.assertEqual(page["type"], "number")
        self.assertEqual(page["label"], "1")
        self.assertTrue(page["active"])

    def test_get_pagination_ten_pages_on_page_1(self):
        request = RequestFactory().get("/")
        context = {"results": {"hits": {"total": {"value": 199}}}, "query": BASIC_QUERY}
        get_pagination(request, context, 1, create_parameters_from_json_query)
        assert 6 == len(context["pages"])

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "1" == page["label"]
        assert page["active"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "2" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "3" == page["label"]

        page = context["pages"].pop(0)
        assert "ellipsis" == page["type"]

        page = context["pages"].pop(0)
        assert "next" == page["type"]

        page = context["pages"].pop(0)
        assert "last" == page["type"]

    def test_get_pagination_ten_pages_on_page_2(self):
        request = RequestFactory().get("/")
        context = {"results": {"hits": {"total": {"value": 199}}}, "query": BASIC_QUERY}
        get_pagination(request, context, 2, create_parameters_from_json_query)
        assert 9 == len(context["pages"])

        page = context["pages"].pop(0)
        assert "first" == page["type"]

        page = context["pages"].pop(0)
        assert "prev" == page["type"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "1" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "2" == page["label"]
        assert page["active"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "3" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "4" == page["label"]

        page = context["pages"].pop(0)
        assert "ellipsis" == page["type"]

        page = context["pages"].pop(0)
        assert "next" == page["type"]

        page = context["pages"].pop(0)
        assert "last" == page["type"]

    def test_get_pagination_ten_pages_on_page_5(self):
        request = RequestFactory().get("/")
        context = {"results": {"hits": {"total": {"value": 199}}}, "query": BASIC_QUERY}
        get_pagination(request, context, 5, create_parameters_from_json_query)
        assert 11 == len(context["pages"])

        page = context["pages"].pop(0)
        assert "first" == page["type"]

        page = context["pages"].pop(0)
        assert "prev" == page["type"]

        page = context["pages"].pop(0)
        assert "ellipsis" == page["type"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "3" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "4" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "5" == page["label"]
        assert page["active"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "6" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "7" == page["label"]

        page = context["pages"].pop(0)
        assert "ellipsis" == page["type"]

        page = context["pages"].pop(0)
        assert "next" == page["type"]

        page = context["pages"].pop(0)
        assert "last" == page["type"]

    def test_get_pagination_ten_pages_on_page_6(self):
        request = RequestFactory().get("/")
        context = {"results": {"hits": {"total": {"value": 199}}}, "query": BASIC_QUERY}
        get_pagination(request, context, 6, create_parameters_from_json_query)
        assert 11 == len(context["pages"])

        page = context["pages"].pop(0)
        assert "first" == page["type"]

        page = context["pages"].pop(0)
        assert "prev" == page["type"]

        page = context["pages"].pop(0)
        assert "ellipsis" == page["type"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "4" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "5" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "6" == page["label"]
        assert page["active"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "7" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "8" == page["label"]

        page = context["pages"].pop(0)
        assert "ellipsis" == page["type"]

        page = context["pages"].pop(0)
        assert "next" == page["type"]

        page = context["pages"].pop(0)
        assert "last" == page["type"]

    def test_get_pagination_ten_pages_on_page_7(self):
        request = RequestFactory().get("/")
        context = {"results": {"hits": {"total": {"value": 199}}}, "query": BASIC_QUERY}
        get_pagination(request, context, 7, create_parameters_from_json_query)
        assert 11 == len(context["pages"])

        page = context["pages"].pop(0)
        assert "first" == page["type"]

        page = context["pages"].pop(0)
        assert "prev" == page["type"]

        page = context["pages"].pop(0)
        assert "ellipsis" == page["type"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "5" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "6" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "7" == page["label"]
        assert page["active"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "8" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "9" == page["label"]

        page = context["pages"].pop(0)
        assert "ellipsis" == page["type"]

        page = context["pages"].pop(0)
        assert "next" == page["type"]

        page = context["pages"].pop(0)
        assert "last" == page["type"]

    def test_get_pagination_ten_pages_on_page_8(self):
        request = RequestFactory().get("/")
        context = {"results": {"hits": {"total": {"value": 199}}}, "query": BASIC_QUERY}
        get_pagination(request, context, 8, create_parameters_from_json_query)
        assert 10 == len(context["pages"])

        page = context["pages"].pop(0)
        assert "first" == page["type"]

        page = context["pages"].pop(0)
        assert "prev" == page["type"]

        page = context["pages"].pop(0)
        assert "ellipsis" == page["type"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "6" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "7" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "8" == page["label"]
        assert page["active"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "9" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "10" == page["label"]

        page = context["pages"].pop(0)
        assert "next" == page["type"]

        page = context["pages"].pop(0)
        assert "last" == page["type"]

    def test_get_pagination_ten_pages_on_page_9(self):
        request = RequestFactory().get("/")
        context = {"results": {"hits": {"total": {"value": 199}}}, "query": BASIC_QUERY}
        get_pagination(request, context, 9, create_parameters_from_json_query)
        assert 9 == len(context["pages"])

        page = context["pages"].pop(0)
        assert "first" == page["type"]

        page = context["pages"].pop(0)
        assert "prev" == page["type"]

        page = context["pages"].pop(0)
        assert "ellipsis" == page["type"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "7" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "8" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "9" == page["label"]
        assert page["active"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "10" == page["label"]

        page = context["pages"].pop(0)
        assert "next" == page["type"]

        page = context["pages"].pop(0)
        assert "last" == page["type"]

    def test_get_pagination_ten_pages_on_page_10(self):
        request = RequestFactory().get("/")
        context = {"results": {"hits": {"total": {"value": 199}}}, "query": BASIC_QUERY}
        get_pagination(request, context, 10, create_parameters_from_json_query)
        assert 6 == len(context["pages"])

        page = context["pages"].pop(0)
        assert "first" == page["type"]

        page = context["pages"].pop(0)
        assert "prev" == page["type"]

        page = context["pages"].pop(0)
        assert "ellipsis" == page["type"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "8" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "9" == page["label"]

        page = context["pages"].pop(0)
        assert "number" == page["type"]
        assert "10" == page["label"]
        assert page["active"]

    def test_pre_2020_sprint_url_compatibility(self):
        response = self.client.get(
            '/search?json_query={"query"%3A+{"bool"%3A+{"must"%3A+{"query_string"%3A+{"query"%3A+"test"%2C+"default_field"%3A+"*"}}%2C+"filter"%3A+[{"bool"%3A+{"should"%3A+[]}}%2C+{"bool"%3A+{"should"%3A+[]}}%2C+{"bool"%3A+{"should"%3A+[]%2C+"must"%3A+{}%2C+"minimum_should_match"%3A+1}}%2C+{"bool"%3A+{"should"%3A+{"range"%3A+{"amountAwarded"%3A+{}}}%2C+"must"%3A+{}%2C+"minimum_should_match"%3A+1}}%2C+{"bool"%3A+{"should"%3A+[]}}%2C+{"bool"%3A+{"should"%3A+[]}}%2C+{"bool"%3A+{"should"%3A+[]}}%2C+{"bool"%3A+{"should"%3A+[]}}]}}%2C+"extra_context"%3A+{"awardYear_facet_size"%3A+3%2C+"amountAwardedFixed_facet_size"%3A+3}%2C+"sort"%3A+{"_score"%3A+{"order"%3A+"desc"}}%2C+"aggs"%3A+{"fundingOrganization"%3A+{"terms"%3A+{"field"%3A+"fundingOrganization.id_and_name"%2C+"size"%3A+3}}%2C+"recipientOrganization"%3A+{"terms"%3A+{"field"%3A+"recipientOrganization.id_and_name"%2C+"size"%3A+3}}%2C+"recipientRegionName"%3A+{"terms"%3A+{"field"%3A+"recipientRegionName"%2C+"size"%3A+3}}%2C+"recipientDistrictName"%3A+{"terms"%3A+{"field"%3A+"recipientDistrictName"%2C+"size"%3A+3}}%2C+"currency"%3A+{"terms"%3A+{"field"%3A+"currency"%2C+"size"%3A+3}}}}'
        )
        assert response.status_code == 200
        assert response.context["text_query"] == "test"

    def test_recipientOrganization_filter_ajax(self):
        uri = reverse_lazy("filter_search_ajax")
        response = self.client.get(
            f"{uri}?parent_field=recipientOrganization&child_field=id_and_name&filter_search=a"
        )
        assert len(json.loads(response.content)["results"]) == 100

    def test_programmeTitle_filter_ajax(self):
        uri = reverse_lazy("filter_search_ajax")
        response = self.client.get(
            f"{uri}?parent_field=grantProgramme&child_field=title_keyword&filter_search=a"
        )
        assert len(json.loads(response.content)["results"]) == 23

    def test_district_filter_ajax(self):
        uri = reverse_lazy("filter_search_ajax")
        response = self.client.get(
            f"{uri}?parent_field=additional_data&child_field=recipientDistrictName&filter_search=a"
        )
        assert len(json.loads(response.content)["results"]) == 73
