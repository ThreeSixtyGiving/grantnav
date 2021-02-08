GrantNav
========



<h2 id="search_box">How does the GrantNav search box work?</h2>
  <p>GrantNav provides a search box which allows you to explore the data. There are four search patterns to choose from:</p>

  <div class="row bottom-space">
    <div class="col-xs-12">
      <table class="table table-condensed table-bordered table-striped dt-responsive" width="100%">
        <thead>
          <tr>
            <th>Search</th>
            <th>Coverage</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Search All</td>
            <td>Searches across all fields of the data, including all text and numbers. To learn more about what fields are present in 360Giving data, see the  <a href="http://standard.threesixtygiving.org">360Giving Data Standard</a>. Data in fields that are provided by publishers but that aren't part of the standard will be included in this search.</td>
          </tr>
          <tr>
            <td>Locations</td>
            <td>
              <p>Searches the ward, district and region location of the recipient organisation, of any grant record which features this geographical information.</p>
              <p>See also: <a href="#location_data">GrantNav and location data</a></p>
            </td>
          </tr>
          <tr>
            <td>Recipients</td>
            <td>Searches the name of the recipient organisation only.</td>
          </tr>
          <tr>
            <td>Titles and Descriptions</td>
            <td>Searches the title and description of the grants only.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>




## Examples

Table without horizontal scrollbar:

```eval_rst
.. list-table::
    :header-rows: 1
    :widths: 1 3 1 1

    * - A
      - B
      - C
      - D
    * - Lorem
      - Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec dictum urna non purus tristique pharetra.
      - Yes
      - False
    * - Ipsum
      - Mauris et lobortis nibh. Nullam vitae velit turpis. Vestibulum facilisis sit amet sapien nec maximus.
      - No
      - True
    * - Dolor
      - Pellentesque sit amet sapien tincidunt, fringilla dui id, porttitor purus. Nam tincidunt ac ex id porttitor. Praesent varius lectus nisl, ac luctus erat lacinia vitae.
      - Yes
      - True
```

### Markdown reference links

Link to [a ref](a-ref).


```eval_rst
.. _a-ref:
```
#### Referenced section

# Markdown inside an admonition

```eval_rst
.. admonition:: Admonition
    :class: hint

    .. markdown::

        Some markdown [a URL](http://example.org), `single backtick literals`.
```

(from <https://sphinxcontrib-opendataservices.readthedocs.io/en/latest/misc/>)


## Contents

```eval_rst
.. toctree::
   :maxdepth: 2

   refining_results
   understanding_results
   advanced_search
   locations
   organizations
   export
   data
   developers


```
