```eval_rst
.. _locations:
```

Understanding Location in GrantNav
==================================

Understanding where a grant is located is one of the most common tasks that GrantNav is used for, and where there is potential for misunderstanding. 

The [360Giving Data Standard](https://standard.threesixtygiving.org/en/latest/reference/) doesn't require that grants contain location data. This is because this isn't data that all grantmakers keep, and it's not always relevant - for example, if a grant relates to policy or research. 

If a grant doesn't have any location information, then it won't show up in searches using the **Locations** search mode, or when using the location-based filters on the search results page. Only UK locations can be searched and filtered using the location functions. To search for locations outside of the UK use 'All grant fields' search option.

Often, grants will contain limited geographical information (such as just a postcode, or a region name), and so GrantNav adds extra detail - such as the name of the ward, district and region that the postcode given is in. Where possible, GrantNav also adds GeoGSS codes from the [ONS Register of Geographic Codes](https://geoportal.statistics.gov.uk/). 

The **Locations** search mode searches for the text given inside the location fields of grants, including those supplied by the publisher, and those added by GrantNav. You can search by the name of a place, or by GeoGSS code. 

GrantNav's **Locations** search mode is text-based, so it won't provide results that are geographically near (or commonly considered to be part of) the place searched for, or distinguish between places that have the same name, or partial name. 

```eval_rst
.. admonition:: Searching for Leeds
    :class: hint

    .. markdown::

        If you're looking for grants in Leeds, Yorkshire, then enter the term "Leeds" and select **Locations** mode for your search. On the results page, you'll notice that there are a handful of grants in the Leeds Ward of Maidstone District on the South-East Coast of England, so use the Recipient District filter to just see results in the Leeds in Yorkshire. 

```

## Recipient vs Beneficiary Location

While the 360Giving Data Standard allows publishers to include beneficiary location data (the place where the funded activity is taking place), many funders find it challenging to determine and record this information in a meaningful way. As a result, it's relatively rare to see this data published. 

To search for grants that contain beneficiary information, use the per-field searching function of the [Search Bar](search-bar)
  