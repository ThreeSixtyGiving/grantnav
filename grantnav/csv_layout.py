from collections import OrderedDict

from grantnav.additional_data import additional_data_schema, flatten_schema_titles

_ADDITIONAL_DATA_PATH_PREFIX = "result.additional_data."

_additional_data_schema_titles = dict(flatten_schema_titles(additional_data_schema))


def additional_data(path):
    schema_path = path[len(_ADDITIONAL_DATA_PATH_PREFIX):]
    field_parts = [part for part in schema_path.split(".") if not part.isdigit()]
    title = _additional_data_schema_titles.get(": ".join(field_parts)) or field_parts[-1]
    return (f"{title} (additional data)", path)


grants_csv = OrderedDict([
    ("Identifier", "result.id"),
    ("Title", "result.title"),
    ("Description", "result.description"),
    ("Currency", "result.currency"),
    ("Amount Applied For", "result.amountAppliedFor"),
    ("Amount Awarded", "result.amountAwarded"),
    ("Amount Disbursed", "result.amountDisbursed"),
    ("Award Date", "result.awardDateDateOnly"),
    ("URL", "result.recipientOrganization.0.url"),

    ("Planned Dates:Start Date", "result.plannedDates.0.startDateDateOnly"),
    ("Planned Dates:End Date", "result.plannedDates.0.endDateDateOnly"),
    ("Planned Dates:Duration (months)", "result.plannedDates.0.duration"),
    ("Actual Dates:Start Date", "result.actualDates.0.startDate"),
    ("Actual Dates:End Date", "result.actualDates.0.endDateDateOnly"),
    ("Actual Dates:Duration (months)", "result.actualDates.0.duration"),

    ("Recipient Org:Identifier", "result.recipientOrganization.0.id"),
    ("Recipient Org:Name", "result.recipientOrganization.0.name"),
    ("Recipient Org:Charity Number", "result.recipientOrganization.0.charityNumber"),
    ("Recipient Org:Company Number", "result.recipientOrganization.0.companyNumber"),
    ("Recipient Org:Postal Code", "result.recipientOrganization.0.postalCode"),
    ("Recipient Org:Location:0:Geographic Code Type", "result.recipientOrganization.0.location.0.geoCodeType"),
    ("Recipient Org:Location:0:Geographic Code", "result.recipientOrganization.0.location.0.geoCode"),
    ("Recipient Org:Location:0:Name", "result.recipientOrganization.0.location.0.name"),
    ("Recipient Org:Location:1:Geographic Code Type", "result.recipientOrganization.0.location.1.geoCodeType"),
    ("Recipient Org:Location:1:Geographic Code", "result.recipientOrganization.0.location.1.geoCode"),
    ("Recipient Org:Location:1:Name", "result.recipientOrganization.0.location.1.name"),
    ("Recipient Org:Location:2:Geographic Code Type", "result.recipientOrganization.0.location.2.geoCodeType"),
    ("Recipient Org:Location:2:Geographic Code", "result.recipientOrganization.0.location.2.geoCode"),
    ("Recipient Org:Location:2:Name", "result.recipientOrganization.0.location.2.name"),

    ("Recipient Individual Id", "result.recipientIndividual.id"),
    ("Recipient Individual Name", "result.recipientIndividual.name"),
    ("Recipient Individual Details:Primary Grant Reason", "result.toIndividualsDetails.primaryGrantReason"),
    ("Recipient Individual Details:Secondary Grant Reason", "result.toIndividualsDetails.secondaryGrantReason"),
    ("Recipient Individual Details:Grant Purpose", "result.toIndividualsDetails.grantPurpose"),

    ("Funding Org:Identifier", "result.fundingOrganization.0.id"),
    ("Funding Org:Name", "result.fundingOrganization.0.name"),
    ("Funding Org:Postal Code", "result.fundingOrganization.0.postalCode"),
    ("Funding Org:Charity Number", "result.fundingOrganization.0.charityNumber"),
    ("Funding Org:Company Number", "result.fundingOrganization.0.companyNumber"),


    ("Grant Programme:Code", "result.grantProgramme.0.code"),
    ("Grant Programme:Title", "result.grantProgramme.0.title"),
    ("Grant Programme:URL", "result.grantProgramme.0.url"),

    ("Grant Type", "result.simple_grant_type"),
    ("Regrant Type", "result.regrantType"),

    ("Funding Type Title", "result.fundingType.0.title"),

    ("Beneficiary Location:0:Name", "result.beneficiaryLocation.0.name"),
    ("Beneficiary Location:0:Country Code", "result.beneficiaryLocation.0.countryCode"),
    ("Beneficiary Location:0:Geographic Code", "result.beneficiaryLocation.0.geoCode"),
    ("Beneficiary Location:0:Geographic Code Type", "result.beneficiaryLocation.0.geoCodeType"),
    ("Beneficiary Location:1:Name", "result.beneficiaryLocation.1.name"),
    ("Beneficiary Location:1:Country Code", "result.beneficiaryLocation.1.countryCode"),
    ("Beneficiary Location:1:Geographic Code", "result.beneficiaryLocation.1.geoCode"),
    ("Beneficiary Location:1:Geographic Code Type", "result.beneficiaryLocation.1.geoCodeType"),
    ("Beneficiary Location:2:Name", "result.beneficiaryLocation.2.name"),
    ("Beneficiary Location:2:Country Code", "result.beneficiaryLocation.2.countryCode"),
    ("Beneficiary Location:2:Geographic Code", "result.beneficiaryLocation.2.geoCode"),
    ("Beneficiary Location:2:Geographic Code Type", "result.beneficiaryLocation.2.geoCodeType"),
    ("Beneficiary Location:3:Name", "result.beneficiaryLocation.3.name"),
    ("Beneficiary Location:3:Country Code", "result.beneficiaryLocation.3.countryCode"),
    ("Beneficiary Location:3:Geographic Code", "result.beneficiaryLocation.3.geoCode"),
    ("Beneficiary Location:3:Geographic Code Type", "result.beneficiaryLocation.3.geoCodeType"),
    ("Beneficiary Location:4:Name", "result.beneficiaryLocation.4.name"),
    ("Beneficiary Location:4:Country Code", "result.beneficiaryLocation.4.countryCode"),
    ("Beneficiary Location:4:Geographic Code", "result.beneficiaryLocation.4.geoCode"),
    ("Beneficiary Location:4:Geographic Code Type", "result.beneficiaryLocation.4.geoCodeType"),
    ("Beneficiary Location:5:Name", "result.beneficiaryLocation.5.name"),
    ("Beneficiary Location:5:Country Code", "result.beneficiaryLocation.5.countryCode"),
    ("Beneficiary Location:5:Geographic Code", "result.beneficiaryLocation.5.geoCode"),
    ("Beneficiary Location:5:Geographic Code Type", "result.beneficiaryLocation.5.geoCodeType"),
    ("Beneficiary Location:6:Name", "result.beneficiaryLocation.6.name"),
    ("Beneficiary Location:6:Country Code", "result.beneficiaryLocation.6.countryCode"),
    ("Beneficiary Location:6:Geographic Code", "result.beneficiaryLocation.6.geoCode"),
    ("Beneficiary Location:6:Geographic Code Type", "result.beneficiaryLocation.6.geoCodeType"),
    ("Beneficiary Location:7:Name", "result.beneficiaryLocation.7.name"),
    ("Beneficiary Location:7:Country Code", "result.beneficiaryLocation.7.countryCode"),
    ("Beneficiary Location:7:Geographic Code", "result.beneficiaryLocation.7.geoCode"),
    ("Beneficiary Location:7:Geographic Code Type", "result.beneficiaryLocation.7.geoCodeType"),
    ("From An Open Call?", "result.fromOpenCall"),
    # ("#comment The following fields are not in the 360 Giving Standard and are added by GrantNav.", ""),
    # Additional data
    ("Data Source", "dataset.distribution.0.downloadURL"),
    ("Publisher Name", "dataset.publisher.name"),

    additional_data("result.additional_data.recipientRegionName"),
    additional_data("result.additional_data.recipientDistrictName"),
    additional_data("result.additional_data.recipientDistrictGeoCode"),
    additional_data("result.additional_data.recipientWardName"),
    additional_data("result.additional_data.recipientWardNameGeoCode"),
    additional_data("result.additional_data.GNBestCountyName"),

    additional_data("result.additional_data.GNRecipientOrgRegionName"),
    additional_data("result.additional_data.GNRecipientOrgRegionGeoCode"),

    additional_data("result.additional_data.GNRecipientOrgDistrictName"),
    additional_data("result.additional_data.GNRecipientOrgDistrictGeoCode"),
    additional_data("result.additional_data.GNRecipientOrgCountyName"),

    additional_data("result.additional_data.GNBeneficiaryRegionName"),
    additional_data("result.additional_data.GNBeneficiaryRegionGeoCode"),
    additional_data("result.additional_data.GNBeneficiaryCountyName"),
    additional_data("result.additional_data.GNBeneficiaryDistrictName"),
    additional_data("result.additional_data.GNBeneficiaryDistrictGeoCode"),

    ("Retrieved for use in GrantNav (additional data)", "dataset.datagetter_metadata.datetime_downloaded"),
    additional_data("result.additional_data.TSGFundingOrgType"),
    additional_data("result.additional_data.GNCanonicalFundingOrgId"),
    additional_data("result.additional_data.GNCanonicalFundingOrgName"),
    additional_data("result.additional_data.TSGRecipientType"),
    additional_data("result.additional_data.recipientOrgInfos.0.dateRegistered"),
    additional_data("result.additional_data.recipientOrgInfos.0.dateRemoved"),
    additional_data("result.additional_data.recipientOrgInfos.0.orgIDs"),
    additional_data("result.additional_data.recipientOrgInfos.0.latestIncome"),
    additional_data("result.additional_data.recipientOrgInfos.0.latestIncomeDate"),
    additional_data("result.additional_data.recipientOrgInfos.0.organisationTypePrimary"),
    additional_data("result.additional_data.recipientOrgInfos.0.postalCode"),
    additional_data("result.additional_data.recipientOrgInfos.0.source"),
    additional_data("result.additional_data.GNCanonicalRecipientOrgId"),
    additional_data("result.additional_data.GNCanonicalRecipientOrgName"),
    additional_data("result.additional_data.metadata.source_license_name"),
    additional_data("result.additional_data.metadata.source_license"),
    additional_data("result.additional_data.metadata.sources_metadata.recipientOrgInfos.license"),
    additional_data("result.additional_data.metadata.sources_metadata.locationLookup.license"),
    additional_data("result.additional_data.metadata.sources_metadata.recipientOrganizationLocation.license"),
    additional_data("result.additional_data.metadata.sources_metadata.codeListLookup.license"),

    ("Date Modified", "result.dateModified"),

    # These two always need to be on the end
    ("License", "dataset.license"),
    ("Note See http://grantnav.threesixtygiving.org/datasets/ for further license information.", ""),
])

grant_csv_titles = list(grants_csv.keys())
grant_csv_paths = list(grants_csv.values())

org_csv_titles = [
    "Grants",
    "Total",
    "Average",
    "Largest",
    "Smallest"
]

recipient_csv_titles = ["Recipient Name", "Recipient ID"] + org_csv_titles
funder_csv_titles = ["Funder Name", "Funder ID"] + org_csv_titles

org_csv_paths = [
    "org_name",
    "org_id",
    "count",
    "sum",
    "avg",
    "max",
    "min"
]


def grants_csv_to_dictionary():
    """ takes grants_csv and turns it into a dictionary of parent/child
    fields e.g.

    res["Planned Dates"] = [
     {'title': 'Start Date', 'path': 'result.plannedDates.0.startDateDateOnly'},
     {'title': 'End Date', 'path': 'result.plannedDates.0.endDateDateOnly'},
     {'title': 'Duration (months)', 'path': 'result.plannedDates.0.duration'}
    ]
    """
    res = {}

    for title, path in grants_csv.items():
        parsed = title.split(":", maxsplit=1)
        # initialise array if needed
        if not res.get(parsed[0]):
            res[parsed[0]] = []

        if len(parsed) > 1:
            display_title = ": ".join(parsed[1:])
        else:
            display_title = title

        res[parsed[0]].append({"title": display_title, "path":
                               path, "column_title": title})

    return res


grants_csv_dict = grants_csv_to_dictionary()
