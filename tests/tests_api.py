import json
import time
import os

from dataload.import_to_elasticsearch import import_to_elasticsearch

from django.test import TestCase, Client
from django.urls import reverse_lazy

prefix = os.path.join(os.path.dirname(__file__), "data")


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
        time.sleep(5)  # Elasticsearch needs some time to commit its data

    def setUp(self):
        """
        This setUp method will be executed before each test method.
        """
        self.client = Client()

    def test_aggregates(self):
        response = self.client.get(reverse_lazy("api:aggregates"))

        res = json.loads(response.content)

        # For updating test data changes and easier comparison
        # with open("/tmp/new_test_data.json", "w") as f:
        #    f.write(json.dumps(res))

        expected_data = json.load(
            open(os.path.join(prefix, "aggregates_expected.json"), "r")
        )

        self.assertEqual(res, expected_data)
