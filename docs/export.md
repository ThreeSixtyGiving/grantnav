Exporting Data From GrantNav
============================

GrantNav offers a range of data exports as CSV or JSON files:

* The entire grants data set
* Search results
* Grants per region, district, funder and recipient 
* Summary data by funder 

## What is included in the GrantNav export files?

### Grants Exports

The JSON files of grants contain all of the data supplied in the original data (both fields from the standard, and any extra fields included by the publisher), plus the [additional data added by the 360Giving pipeline](additional-fields). 

The CSV files of grants contain all of the required fields from the 360Giving standard, the most commonly-used optional fields from the standard, plus some commonly-used fields from the data added by the 360Giving pipeline. Columns may be entirely blank if no grant in your download uses a particular field; individual rows may have blank fields if the source data doesn't contain that field. 

Because the export files use the [360Giving Standard](https://standard.threesixtygiving.org/en/latest/) you can use the standard reference to understand the meaning and contents of the fields. 


### Funder Summary Exports

The funder page provides summary statistics on recipients who have been funded by that funder. These statistics can be exported. The files contain 

The JSON and CSV files for the recipient and funder pages contain all of the fields that are visible in the tables in GrantNav, plus an extra column containing the organisation ID:

```eval_rst
.. list-table::
    :header-rows: 1
    :widths: 1 3

        * - Field
          - Description
        * - Funder / Recipient
          - Funder or recipient name
        * - Funder Id / Recipient Id
          - Identifier code of the funder or recipient
        * - Grants
          - Number of grants made by/to the funder or recipient
        * - Total
          - Total value of all grants made by/to the funder or recipient
        * - Average
          - Average value of a grant made by/to the funder or recipient
        * - Largest
          - Value of the largest grant made by/to the funder or recipient
        * - Smallest
          - Value of the smallest grant made by/to the funder or recipient

```


Note that export files can be very large - in particular the whole dataset is several hundred MB, and large search results can be a similar size. Refining your search or splitting up your export can help, but be aware of the constraints around [refining search results](refining-results)


```eval_rst
.. _additional-fields:
```

## Fields added by the 360Giving pipeline

The following fields are not in the 360Giving Data Standard and are added to the export data by the 360Giving pipeline:


```eval_rst
.. list-table::
    :header-rows: 1
    :widths: 1 3

    * - Field
      - Description
    * - Data Source
      - This is the URL (web link) for the data file containing this grant record.
    * - Publisher:Name
      - This is the name of the organisation publishing the data file. This data is held centrally by 360Giving.
    * - Recipient Region
      - This is the name of the geographic area at Region level, added by GrantNav (see <a href="#location_data">GrantNav and location data</a> for explanation).
    * - Recipient District
      - This is the name of the geographic area at District level, added by GrantNav (see <a href="#location_data">GrantNav and location data</a> for explanation).
    * - Recipient Ward
      - This is the name of the geographic area at Ward level, added by GrantNav (see <a href="#location_data">GrantNav and location data</a> for explanation).
    * - Retrieved for use in GrantNav
      - This is the date and time the data was accessed for use in GrantNav.
    * - License (see note below)
      - The URL (web link) to the specific licence under which the data file containing this grant record was published.

```

```eval_rst
.. _funder-summary-fields:
```

## Fields available on the Funder and Recipient page exports



