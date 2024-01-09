```eval_rst
.. _locations:
```

Understanding Location in GrantNav
==================================

Understanding where a grant is located is one of the most common tasks that GrantNav is used for, and where there is potential for misunderstanding.

The [360Giving Data Standard](https://standard.threesixtygiving.org/en/latest/reference/) doesn‘t require that grants contain location data. This is because this isn‘t data that all grantmakers keep, and it‘s not always relevant – for example, if a grant relates to policy or research.

If a grant doesn‘t have any location information, then it won‘t show up in searches using the **Locations search mode** of the [Search Bar](https://help.grantnav.threesixtygiving.org/en/latest/search_bar/#search-bar), or when using the **Geography filters** on the search results page. Only UK locations can be searched and filtered using these location functions. To search for locations outside of the UK, use the ‘All grant fields‘ search mode of the Search Bar.

When a grant does include location information, in the form of a postcode or [ONS Geographic Codes](https://geoportal.statistics.gov.uk/), GrantNav uses this data to power its Location functions, populating the name and geocodes of the Ward, District and Region that the provided location is in, where possible.

The **Geography filters** in the left hand side use the location data to allow filtering by UK Country and English Region or by District.

The **Locations search mode** of the Search Bar allows searches by UK Country and English Region and District names or geocodes.

The UK Country and English Region name and District and Ward names and geocode data is also included in GrantNav search result downloads in fields labelled “Additional data”.

GrantNav‘s **Locations search mode** is based on the names or geocodes from official ONS sources, so it won‘t provide results that are geographically near (or commonly considered to be part of) the place searched for, or distinguish between places that have the same name, or partial name.

## Recipient vs Beneficiary Location

The 360Giving Data Standard allows publishers to include both **Recipient Location** (the place where the Recipient Organisation is based) and **Beneficiary Location** data (the place where the funded activity is taking place). While over two thirds of publishers share some form of Recipient Location, funders find it more challenging to determine and record Beneficiary Location information. As a result, only one third publish Beneficiary Location data that can be used by GrantNav. You can learn more about how many publishers and the proportion of grants with Recipient location and Beneficiary location (known as grant location) in our [Quality Dashboard](https://qualitydashboard.threesixtygiving.org/alldata).

Because a Beneficiary Location usually provides a more accurate way to answer the question ‘Where do grants go?’ than a Recipient location, the Location search bar and filters use either Beneficiary or Recipient Location data shared by publishers, with priority given to Beneficiary Location where both are available.
