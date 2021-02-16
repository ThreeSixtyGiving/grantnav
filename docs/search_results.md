```eval_rst
.. _search-results:
```

Search Results
==============

GrantNav's search is designed to give helpful, accurate results, but there are ways in which GrantNav differs from general-purpose web search engines such as Google and DuckDuckGo. 

## GrantNav doesn't attempt semantic matching

When you search for a word in a general-purpose search engine, it tries to work out what you mean by that word; this is called semantic matching. For example, a Google search for "youth clubs" will return results for "young people's centres".

GrantNav is faithful to the text of the grant record, and so doesn't attempt to do this. As a result, you might find more relevant grants if you search for other names that the thing that you're looking for might be called. 

## GrantNav includes results that only match some of your search

GrantNav results include grants that only match some, or one, of the search terms that you put in, unless you've used the AND keyword. It will also include results with words that are similar to the one that you provided using stemming. 

As a result, a search for "activities for disabled boys" will match a grant providing "support for carers of women with disabilities", because "disabilities" is recognised as having the same root as "disabled". The match will be very low down in the results, however, because it's only matching one word, and it's matching a different form of the word. This result will, however, still be included in the summary statistics, so these should be treated with caution until you've been able to review the data. 

## GrantNav only includes grants that contain the fields required for your filter

GrantNav's filters show the grants which contain the selected value in the relevant field. If the publisher of the data hasn't included that data, then GrantNav's filters will exclude the grant, even if it appears that it should be included. 

For example, if you filter by "Recipient Region", then all grants that don't have any recipient location data will be excluded from the search.

If grants that you are expecting are missing, you could contact the publisher of the data (usually the funder) to enquire about whether they provide the relevant data. The [360Giving Registry](https://data.threesixtygiving.org) provides a full list of organisations and their contact details

## GrantNav doesn't try to work out locations that aren't specified

Organisations publishing data using the 360Giving standard have the opportunity to provide accurate location data for their grants, using a variety of mechanisms. If they don't provide this data, then GrantNav can't work out where the grants are located. 

General-purpose search engines often use lots of other data that's available on the Web to make a best-effort guess at where you're referring to. 

For example, if a grant is to the “Lancaster Rowing Club” but the grant doesn’t contain any recipient location data, then using the recipient region filter to select ‘North West’ will exclude the grant from the results, because GrantNav doesn't use any external data to work out that the "Lancaster" in the name of the club is the name of a city, nor does it make an attempt to work out where Lancaster is. 

This is a design choice to encourage the publication of comprehensive data, and to avoid misleading results where there are common place names - there are at least 10 Newports in the UK!   

## Some grantmakers publish grants with £0 or negative values

Publishers sometimes set the grant value to be £0 for accounting reasons, or to signify something about the grant (such as that it was regranted). Refer to the relevant organisation website for the dataset for further information about their data, and to contact them for clarification. 

These values are accounted for when generating the summary statistics. 