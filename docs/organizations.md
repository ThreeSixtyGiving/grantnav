Understanding Organizations in GrantNav
=======================================

<h3 id="charity_names">GrantNav and charity names</h3>
  <p>It’s useful for people to see multiple grants associated with a single organization together in GrantNav. To do this, we rely on publishers to include the relevant company, charity or other registration number in the Recipient Org:Identifier
    field.</p>

  <p>When we import data into GrantNav, we aim to match these identifiers, in order to provide pages that bring together grants from different publishers, even if they spell the recipient names differently.</p>

  <p>When we undertook research to do this, we found that quite often registered charities were given different names by various publishers. Even if the Recipient Org:Identifier reference were exactly the same, the name given was often different,
    e.g. “Salford Lads Club” vs “Salford Lads & Girls Club”.</p>

  <p>In order to help users, we therefore <a href="http://grantnav.threesixtygiving.org/datasets/">utilise the data</a> available from the <a href="http://data.charitycommission.gov.uk/default.aspx">Charity Commission for England and Wales</a>, if the recipient is registered. We look for the official name on this register. With this, we populate the Recipient Org:Name field, which in turn is
    used in the relevant filter on GrantNav. However, we also maintain the original name from the publisher, and use that in the grant page and freetext search.</p>