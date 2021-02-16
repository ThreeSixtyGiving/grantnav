Understanding Location in GrantNav
==================================

  <h2 id="beneficiary_data">Why do GrantNav filters show recipient rather than beneficiary location?</h2>
  <p>While the 360Giving Data Standard allows publishers to include beneficiary location data (the place where funded activity is taking place), it can sometimes be hard to determine and record this information in a meaningful way, and so not all data includes this type of information. When there is beneficiary location information available about a grant you will find this data on the grant page and included in the data download.</p>


  <h3 id="location_data">GrantNav and location data</h3>
  <p>When we import this data, we look at the Location information associated with the Recipient Organisation. This data can vary across publishers.</p>

    <h4>When a Recipient Org:Postal Code is provided</h4>
  <p>We use the postcode to add Ward, District and Region codes to the data. This is used in the relevant filters in GrantNav, and also Ward, District and Region names are included in the download files. To see the datasets used, see <a href="/datasets/">Data used in GrantNav</a></p>

  <h4>When a Recipient Org:Postal Code is missing</h4>
  <p>If other types of administrative geography are included in the data (such as District or Ward codes) then we attempt to match it to relevant areas. Again, these are used in the filters and the names and codes are included in the download files.</p>


  TODO: Talk about location augmentation
  