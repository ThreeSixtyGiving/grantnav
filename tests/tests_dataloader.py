import json
import os

from dataload.import_to_elasticsearch import (
    update_doc_with_other_locations,
    update_doc_with_undetermined,
    update_doc_with_geo_category,
)

from django.test import TestCase

prefix = os.path.join(os.path.dirname(__file__), "data")


class DataLoaderTest(TestCase):

    def test_gn_additional_location_fields_international_grant(self):
        """check that the GN* location related fields we are expecting from
        update_doc_with_other_locations are present"""
        grant_data = json.load(
            open(os.path.join(prefix, "international_grant_GN_location_fields.json"))
        )

        update_doc_with_other_locations(grant_data)
        update_doc_with_undetermined(grant_data)

        # These new fields should appear with the following values
        GN_location_fields = [
            ("GNBeneficiaryCountryName", "Uganda"),
            ("GNRecipientOrgCountyName", "Lambeth"),
            ("GNRecipientOrgDistrictName", "Lambeth"),
            ("GNRecipientOrgDistrictGeoCode", "E09000022"),
            ("GNRecipientOrgRegionName", "London"),
            ("GNRecipientOrgRegionGeoCode", "E12000007"),
            (
                "GNRecipientOrgCountryName",
                "United Kingdom of Great Britain and Northern Ireland",
            ),
            ("GNBestCountyName", "Lambeth"),
            ("GNBestCountryName", "Uganda"),
            ("GNBeneficiaryDistrictName", "Undetermined"),
            ("GNBeneficiaryRegionName", "Undetermined"),
            ("GNBeneficiaryCountyName", "Undetermined"),
        ]

        for field, val in GN_location_fields:
            self.assertEqual(grant_data["additional_data"][field], val)

    def test_gn_additional_location_fields_uk_grant(self):
        """check that the GN* location related fields we are expecting from
        update_doc_with_other_locations are present"""
        grant_data = json.load(
            open(os.path.join(prefix, "uk_grant_GN_location_fields.json"))
        )

        update_doc_with_other_locations(grant_data)
        update_doc_with_undetermined(grant_data)

        # These new fields should appear with the following values
        GN_location_fields = [
            (
                "GNBeneficiaryCountryName",
                "United Kingdom of Great Britain and Northern Ireland",
            ),
            ("GNBeneficiaryDistrictName", "Southwark"),
            ("GNBeneficiaryDistrictGeoCode", "E09000028"),
            ("GNBeneficiaryCountyName", "Southwark"),
            ("GNBeneficiaryRegionName", "London"),
            ("GNBeneficiaryRegionGeoCode", "E12000007"),
            ("GNBestCountyName", "Southwark"),
            ("GNRecipientOrgRegionName", "London"),
            ("GNRecipientOrgRegionGeoCode", "E12000007"),
            (
                "GNRecipientOrgCountryName",
                "United Kingdom of Great Britain and Northern Ireland",
            ),
            ("GNRecipientOrgCountyName", "Bromley"),
            ("GNRecipientOrgDistrictName", "Bromley"),
            ("GNRecipientOrgDistrictGeoCode", "E09000006"),
            (
                "GNBestCountryName",
                "United Kingdom of Great Britain and Northern Ireland",
            ),
        ]

        for field, val in GN_location_fields:
            self.assertEqual(grant_data["additional_data"][field], val)

    def test_geo_category_uk_grant(self):
        """Check that UK grants are categorized correctly"""
        grant_data = json.load(
            open(os.path.join(prefix, "uk_grant_GN_location_fields.json"))
        )

        update_doc_with_other_locations(grant_data)
        update_doc_with_undetermined(grant_data)
        update_doc_with_geo_category(grant_data)

        self.assertEqual(grant_data["additional_data"]["GNGeoCategory"], "UK")

    def test_geo_category_international_grant(self):
        """Check that international grants are categorized correctly"""
        grant_data = json.load(
            open(os.path.join(prefix, "international_grant_GN_location_fields.json"))
        )

        update_doc_with_other_locations(grant_data)
        update_doc_with_undetermined(grant_data)
        update_doc_with_geo_category(grant_data)

        self.assertEqual(grant_data["additional_data"]["GNGeoCategory"], "International")

    def test_geo_category_undetermined_grant(self):
        """Check that grants with undetermined location are categorized correctly"""
        grant_data = {
            "id": "test-grant-123",
            "additional_data": {},
        }

        update_doc_with_undetermined(grant_data)
        update_doc_with_geo_category(grant_data)

        self.assertEqual(grant_data["additional_data"]["GNGeoCategory"], "Undetermined")
