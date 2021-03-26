# Adding a facet to filter on

Facets are defined in `frontend/views.py`

There are multiple types of facets: Terms, Amount, Date and Non-Terms.

## Add a Terms Facet

1. Add an entry to `BASIC_FILTER` array, this contains the filtering mechanism to be used by elasticsearch. For example: `{"bool": {"should": []}}`

2. Add a `TermFacet` to the `TERM_FACETS` array. The fields for a `TermFacet` are

* `field_name` - The field in the elastic document
* `param_name` - The parameter that will be used in the url
* `filter_index` - The location of this filter mechanism in `BASIC_FILTER`
* `display_name` - Facet name displayed in the template
* `is_json` - Whether the value in `field_name` is in json format

Example:
```
 TermFacet("additional_data.TSGFundingOrgType", "fundingOrganizationTSGType", 8, "Organisation Type", False, False),
 ```

 1. Add a panel to display the facet filter information in `frontend/templates/search.html`. Note the field name in the template context is the `param_name`.

Example:
```html
      <div class="panel panel-default">
        <a class="anchor" id="TSGOrganizationType"></a>
        <div class="panel-heading list-group-compact">
          Funding Organisation Type {% if results.aggregations.fundingOrganizationTSGType.clear_url %} <a href="{{results.aggregations.currency.clear_url}}"> <small>(clear)</small></a> {% endif%}
        </div>
        <div class="list-group">
          {% for bucket in results.aggregations.fundingOrganizationTSGType.buckets %}
            <a href="{{bucket.url}}" class="list-group-item list-group-compact {% if bucket.selected %}list-group-item-success{%endif%}"> {{bucket.key}} <small>({{bucket.doc_count|get_amount}})</small> </a>
          {% endfor %}
          {% if results.aggregations.fundingOrganizationTSGType.buckets|length > 2 %}
            <a href="{{see_more_url.fundingOrganizationTSGType.url}}" class="list-group-item list-group-compact see-more"> <b>{% if see_more_url.fundingOrganizationTSGType.more%}See More{% else %}See Less{% endif %}</b> </a>
          {% endif %}
        </div>
      </div>

```

## Other types of Facet

Other types of facets are added by writing custom functions which require, a create function such as `create_amount_aggregate` , a get function such as `get_amount_facet_fixed` to get the data into the context. Some also have predefined entries in the `BASIC_QUERY`.
