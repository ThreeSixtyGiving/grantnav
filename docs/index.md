GrantNav
========

## Search, explore and download UK grants data published by funders in the 360Giving Data Standard.

```eval_rst
.. admonition::
    :class: hint

    .. markdown::

        GrantNav contains data published by over 175 funders in the UK, including several of the largest grant-makers. Data that is listed on the [360Giving Registry](https://data.threesixtygiving.org/) is downloaded every night, and added to GrantNav, as long as it uses the standard. To learn more about data in Grantnav, see [Data](data.html)
```

GrantNav lets you search for words within grants that have been published by funders, and then refine your search in various ways. From your search results, you can click through to see individual grants, or download the results for further analysis. 

## The Search Bar

On the home page and at the top of the results page, there's a large search box. GrantNav will look for whatever you enter here in the text of grants - including titles, descriptions and locations. 

Below the search bar, you can select from four search modes. 

**All the data** helps when you're looking for as much information as you can find, to filter later. This will look in all the text in the grants. This might mean that you get some irrelevant results, but you're unlikely to miss anything. 

For example, if you search for "Manchester", then you'll see grants that have a location in Manchester, as well as organisations that have Manchester in their name. Generally, it's best to start with an **All the data** search, and then to select a different search mode if you find that there are too many irrelevant results.

**Locations** mode will search within just the location (ward, district and region) information in grants. This will exclude any grants that haven't supplied a location at all, or any grants which have a wider location scope than your search (e.g. a grant for Scotland won't appear in a search for Glasgow).

**Recipients** mode searches just within the names of the recipient organisations. This can be particularly helpful if you're looking for an organisation that you already know the name of, or if you're looking for organisations that are likely to be descriptively named.

**Titles & Descriptions** mode searches just within the titles and descriptions of grants. This can help to avoid inadvertently matching within other fields that aren't relevant. 

For more information on how to use the Search bar, including how to search for phrases, dates, values, ranges and use fuzzy matching, see [Search Bar](search_bar.html)

## Search Results 

GrantNav will search for the words that you enter into the search bar within the scope that you select, and then display the results that it finds. If you've searched for multiple words, then it will display grants that contain all of the words, then grants that contain only some of the words. Grants that contain the search terms multiple times appear higher up. 

```eval_rst
.. admonition:: Irrelevant results
    :class: hint

    .. markdown::

        If your search matches lots of results, then even though the ones on the first page are relevant to you, the ones further down might not be. If you're using search results for research or statistical work, be sure to check the bottom of the results to make sure that the entries there are relevant. 
```

To learn more about how the search results are compiled, see [Search Results](search_results)


## Filtering

On the left-hand side of the search results page are a number of filters which let you see only the grants that meet the specified criteria. 


```eval_rst
.. admonition:: Missing Results
    :class: hint

    .. markdown::

        If a grant doesn't contain the information that a filter uses to work out which results to display, then GrantNav won't include it in the results for that filter. Because the 360Giving data standard doesn't require locations for every grant, grants that don't contain location information won't ever appear in searches that are filtered for location. 
```

To see what all the filters do, see [Refining Results](refining_results)

## Download Results

GrantNav helps you find a set of results, which can be exported for analysis in spreadsheet software or statistical packages. At the top-right of each set of search results are download links for .csv and .json format downloads of the data. 

The .csv file contains the mostly commonly-requested fields, while the .json file contains the full grant records. To learn more, see [Exporting Data](export.html)

## Organisation Pages

It can be helpful to see all of the grants given or received by a single organisation on one page. You can click on the names of funders and recipients throughout GrantNav to see all of the grants that they've given or received. 

```eval_rst
.. admonition:: Identifying Organisations
    :class: hint

    .. markdown::

        Organisations aren't always identified in the same way by funders when they publish their data. This is especially common when an organisation has multiple identifiers (such as when a company is a registered charity) or if an organisation has changed its form over time. The organisation pages are based on the organisation's IDs, rather than name. 

        If you're looking to see all of the grants given to or by an organisation, then a combination of the organisation ID pages and search will help you to find all of the grants in GrantNav. 
```

To learn more about organisations in GrantNav, see [Organisations](organisations)

## Location Pages 

GrantNav has a page for each location - at ward, district and region levels - that lists all grants that have location data included. 

To learn more about locations in GrantNav, see [Locations](locations)


## Contents

```eval_rst
.. toctree::
   :maxdepth: 2

   refining_results
   understanding_results
   search_bar
   locations
   organizations
   export
   data
   developers


```
