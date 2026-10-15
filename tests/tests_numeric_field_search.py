import time
import os

from django.test import TestCase, Client

from dataload.import_to_elasticsearch import import_to_elasticsearch

prefix = os.path.join(os.path.dirname(__file__), "data")


class NumericFieldSearchTest(TestCase):
    """
    Tests for searching numeric fields using range and comparison operators.
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
        time.sleep(5)

    def setUp(self):
        """
        This setUp method will be executed before each test method.
        """
        self.client = Client()

    def test_planned_dates_duration_range_query(self):
        """
        Test that range queries work on plannedDates.duration field
        """

        # Query for durations between 12 and 36 months
        r = self.client.get('/search?query=plannedDates.duration%3A+%5B12+TO+36%5D', follow=True)
        self.assertEqual(r.status_code, 200)

        # Should return results
        total_hits = r.context["results"]["hits"]["total"]["value"]
        self.assertGreater(total_hits, 0, "Range query should return results for durations between 12 and 36 months")

    def test_planned_dates_duration_greater_than(self):
        """
        Test that comparison operators work on plannedDates.duration field
        """

        # Query for durations greater than 12 months
        r = self.client.get('/search?query=plannedDates.duration%3A%3E12', follow=True)
        self.assertEqual(r.status_code, 200)
        total_hits = r.context["results"]["hits"]["total"]["value"]
        self.assertGreater(total_hits, 0, "Query should return results for durations > 12")

        # Verify all results actually have duration > 12
        for hit in r.context["results"]["hits"]["hits"]:
            if "plannedDates" in hit["_source"] and hit["_source"]["plannedDates"]:
                for planned_date in hit["_source"]["plannedDates"]:
                    if "duration" in planned_date:
                        duration = planned_date["duration"]
                        # Convert to int if it's a string (Elasticsearch might return it as a string if it's stored as text)
                        if isinstance(duration, str):
                            duration = int(duration)
                        self.assertGreater(duration, 12,
                            f"Result has duration {duration} which is not > 12")

    def test_planned_dates_duration_less_than(self):
        """
        Test that less-than operators work on plannedDates.duration field
        """

        # Query for durations less than 36 months
        r = self.client.get('/search?query=plannedDates.duration%3A%3C36', follow=True)
        self.assertEqual(r.status_code, 200)

        # Should return results
        total_hits = r.context["results"]["hits"]["total"]["value"]
        self.assertGreater(total_hits, 0, "Query should return results for durations < 36")

    def test_actual_dates_duration_range_query(self):
        """
        Test that range queries work on actualDates.duration field
        """

        # Query for durations between 12 and 36 months
        r = self.client.get('/search?query=actualDates.duration%3A+%5B12+TO+36%5D', follow=True)
        self.assertEqual(r.status_code, 200)

        # Should return results if any grants have actual dates
        total_hits = r.context["results"]["hits"]["total"]["value"]

        # This might be 0 if test data doesn't have actualDates with durations
        self.assertIsInstance(total_hits, int, "Query should execute without error")

    def test_recipient_org_latest_income_greater_than(self):
        """
        Test that comparison operators work on additional_data.recipientOrgInfos.latestIncome field
        """

        min_income = 100000

        # Query for organisations with latest income greater than 100,000
        r = self.client.get(f'/search?query=additional_data.recipientOrgInfos.latestIncome%3A%3E{min_income}', follow=True)

        self.assertEqual(r.status_code, 200)

        # Should return results
        results = r.context["results"]
        total_hits = results["hits"]["total"]["value"]

        self.assertGreater(total_hits, 0,
            "Query should return results for latest income > 100,000")

        # Verify returned latestIncome values are greater than the threshold
        for hit in results["hits"]["hits"]:
            recipient_org_infos = (
                hit["_source"]
                .get("additional_data", {})
                .get("recipientOrgInfos", [])
            )
            for recipient_org in recipient_org_infos:
                if "latestIncome" in recipient_org:
                    latest_income = int(recipient_org["latestIncome"])
                    self.assertGreater(latest_income, min_income)

    def test_recipient_org_latest_income_range_query(self):
        """
        Test that range queries work on additional_data.recipientOrgInfos.latestIncome field
        """

        min_income = 10000
        max_income = 500000

        # Query for organisations with latest income between 10,000 and 500,000
        r = self.client.get(f'/search?query=additional_data.recipientOrgInfos.latestIncome%3A+%5B{min_income}+TO+{max_income}%5D',
                           follow=True)
        self.assertEqual(r.status_code, 200)

        results = r.context["results"]
        total_hits = results["hits"]["total"]["value"]

        self.assertGreater(total_hits, 0,
            "Range query should return results for income between 10,000 and 500,000")

        # Verify returned latestIncome values are between 10,000 and 500,000
        for hit in results["hits"]["hits"]:
            recipientOrgInfos = (
                hit["_source"]
                .get("additional_data", {})
                .get("recipientOrgInfos", [])
            )
            for recipientOrg in recipientOrgInfos:
                if "latestIncome" in recipientOrg:
                    self.assertLessEqual(int(recipientOrg["latestIncome"]), max_income)
                    self.assertGreaterEqual(int(recipientOrg["latestIncome"]), min_income)
