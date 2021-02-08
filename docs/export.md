Exporting Data From GrantNav
============================

<h2 id="export_files">What is included in the GrantNav export files?</h2>
  <p>You can export data from GrantNav searches, and from views of funders and recipients, in either CSV or JSON formats. You can also <a href="/developers/">download the whole data set</a> used in GrantNav.</p>

  <h3 id="export_search">Exporting from a search</h3>
  <p>When you export data from a GrantNav search the download uses the same field names as the <a href="http://standard.threesixtygiving.org/en/latest/">360Giving Data Standard</a>. This is provided in a single file - in the case of the CSV
    file there will be multiple columns for fields that may have more than one value for some grants, such as geographic terms. Please note that not all fields in the 360Giving Data Standard are included in the GrantNav export CSV.
  </p>
  <p>The CSV file contains more fields than are used by core GrantNav functionality, including fields such as beneficiary location data, if this has been provided by the publisher(s). Columns may be entirely blank if no grant in your download uses a particular field. Sometimes, publishers add more fields to the standards for their own use. Such fields are not included in the CSV export, but are included in the JSON export.  
  </p>

  <p>The following fields are not in the 360Giving Data Standard and are added to the export data by GrantNav:</p>

  <div class="row bottom-space">
    <div class="col-xs-12">
      <table class="table table-condensed table-bordered table-striped dt-responsive" width="100%">
        <tr>
          <th>Field</th>
          <th>Description</th>
        </tr>
        <tr>
          <td>Data Source</td>
          <td>This is the URL (web link) for the data file containing this grant record.</td>
        </tr>
        <tr>
          <td>Publisher:Name</td>
          <td>This is the name of the organisation publishing the data file. This data is held centrally by 360Giving.</td>
        </tr>
        <tr>
          <td>Recipient Region</td>
          <td>This is the name of the geographic area, added by GrantNav (see <a href="#location_data">GrantNav and location data</a> for explanation).</td>
        </tr>
        <tr>
          <td>Recipient District</td>
          <td>This is the name of the geographic area, added by GrantNav (see <a href="#location_data">GrantNav and location data</a> for explanation).</td>
        </tr>
        <tr>
          <td>Recipient Ward</td>
          <td>This is the name of the geographic area, added by GrantNav (see <a href="#location_data">GrantNav and location data</a> for explanation).</td>
        </tr>
        <tr>
          <td>Retrieved for use in GrantNav</td>
          <td>This is the date and time the data was accessed for use in GrantNav.</td>
        </tr>
        <tr>
          <td>License (see note below)</td>
          <td>The URL (web link) to the specific licence under which the data file containing this grant record was published.</td>
        </tr>
      </table>
    </div>
  </div>

  <h3 id="export_funders_recipients">Exporting from the funders and recipients pages</h3>
  <p>Data downloaded from the <a href="/funders/">funders</a> and <a href="/recipients/">recipients</a> pages contain only the details seen on screen, plus an extra column
    with the funder or recipient identifiers.</p>

  <div class="row bottom-space">
    <div class="col-xs-12">
      <table class="table table-condensed table-bordered table-striped dt-responsive" width="100%">
        <tr>
          <th>Field</th>
          <th>Description</th>
        </tr>
        <tr>
          <td>Funder / Recipient</td>
          <td>Funder or recipient name</td>
        </tr>
        <tr>
          <td>Funder Id / Recipient Id</td>
          <td>Identifier code of the funder or recipient</td>
        </tr>
        <tr>
          <td>Grants</td>
          <td>Number of grants made by/to the funder or recipient</td>
        </tr>
        <tr>
          <td>Total</td>
          <td>Total value of all grants made by/to the funder or recipient</td>
        </tr>
        <tr>
          <td>Average</td>
          <td>Average value of a grant made by/to the funder or recipient</td>
        </tr>
        <tr>
          <td>Largest</td>
          <td>Value of the largest grant made by/to the funder or recipient</td>
        </tr>
        <tr>
          <td>Smallest</td>
          <td>Value of the smallest grant made by/to the funder or recipient</td>
        </tr>
      </table>
    </div>
  </div>

  <h2 id="exported_data">Working with the exported data</h2>
  <p> Since the data is presented in a standard format, it is pretty clean and ready to use. We recommend you import it to your favourite data analysis tool (like PowerBI or Tableau) and work from there. Depending on your search, some exported data can be very large, so it might take some time to load on Google Sheets or Microsoft Excel. See <a href="http://www.threesixtygiving.org/news-2/">our blog</a> for more ideas of what you can do with the data.  </p>