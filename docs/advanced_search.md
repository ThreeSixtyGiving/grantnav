<h2 id="advanced_search">Advanced search</h2>

  <p>In addition to the freetext search, there are many ways you can search the data on this site and target your search with more specific controls. You can click on the examples to see how they work</p>

  <h3 id="words_phrases">Words and phrases</h3>
  <ul>
    <li class="red_underline"> A single word: e.g. <a href="https://grantnav.threesixtygiving.org/search?text_query=people"><code>people</code></a> </li>
    <li class="red_underline"> Multiple words: e.g. <a href="https://grantnav.threesixtygiving.org/search?text_query=young+people+gardens"><code>young people gardens</code></a> (each word does not necessarily have to be present) </li>
    <li class="red_underline"> Require each word to be found: e.g. <a href="https://grantnav.threesixtygiving.org/search?text_query=young+AND+people"><code>young AND people</code></a> </li>
    <li class="red_underline"> An exact phrase by enclosing it in quotes: e.g. <a href="https://grantnav.threesixtygiving.org/search?text_query=%22young+people%22"><code>"young people"</code></a> </li>
    <li class="red_underline"> Exclude results that contain a word: e.g. <a href="https://grantnav.threesixtygiving.org/search?text_query=youth+NOT+clubs"><code>youth NOT clubs</code></a> </li>
  </ul>

  <p>Using the above you can effectively filter the records to a single organisation or an exact grant. Try:</p>
  <ul>
    <li class="red_underline"><a href="https://grantnav.threesixtygiving.org/search?text_query=%22The+Dulverton+Trust%22"><code>"The Dulverton Trust"</code></a></li>
    <li class="red_underline"><a href="https://grantnav.threesixtygiving.org/search?text_query=%22360G-wolfson-19750%22"><code>"360G-wolfson-19750"</code></a></li>
  </ul>

  <h3 id="fields">Fields</h3>
  <ul>
    <li>Search words and phrases limited to a specific field, for example:
      <ul>
        <li class="red_underline"><a href="https://grantnav.threesixtygiving.org/search?text_query=title:gardens"><code>title:gardens</code></a> will search the "title" field for the word "gardens"</li>
        <li class="red_underline"><a href="https://grantnav.threesixtygiving.org/search?text_query=recipientOrganization.postalCode:NW1"><code>recipientOrganization.postalCode:NW1</code></a> will search the for recipients within the "NW1" postcode district (where the field is populated)</li>
        <li class="red_underline"><a href="https://grantnav.threesixtygiving.org/search?text_query=fundingOrganization.name:%22London Councils%22"><code>fundingOrganization.name:"London Councils"</code></a> will search the "Funding Organisation:Name" field for "London Councils"</li>
      </ul>
    </li>
  </ul>

  <p>The field names used must match the machine-readable field names in the data.</p>

  <h3 id="ranges">Ranges</h3>
  <h4>Dates</h4>

  <p>To search for grants in a given date range:</p>

  <ul>
    <li class="red_underline"> Award date in FY17/18: e.g. <a href="https://grantnav.threesixtygiving.org/search?text_query=awardDate:[2017-04-01 TO 2018-03-31]"><code>awardDate:[2017-04-01 TO 2018-03-31]</code> </a></li>
    <li class="red_underline">Planned start date in 2016: e.g. <a href="https://grantnav.threesixtygiving.org/search?text_query=plannedDates.startDate:[2016-01-01 TO 2016-12-31]"><code>plannedDates.startDate:[2016-01-01 TO 2016-12-31]</code></a></li>
    <li class="red_underline">
       Planned start date in 2015 <strong>and</strong> planned end date in 2017: e.g.
      <a href="https://grantnav.threesixtygiving.org/search?text_query=plannedDates.startDate:[2015-01-01 TO 2015-12-31] AND plannedDates.endDate:[2017-01-01 TO 2017-12-31]">
        <code>plannedDates.startDate:[2015-01-01 TO 2015-12-31] AND plannedDates.endDate:[2017-01-01 TO 2017-12-31]</code>
      </a>
    </li>
  </ul>

  <p>Searching for a range of dates works alongside the Award Date <a href="#filters">filter</a>. Therefore, you can search for a wide date range and then refine, compare or see an overview of the distribution using the filter.

  <h4>Amounts</h4>
  <p>Search for grants by amount (awarded, applied for etc.) within a specific range:</p>
  <ul>
    <li class="red_underline">Amount Awarded between £0 and £150: e.g. <a href="https://grantnav.threesixtygiving.org/search?text_query=amountAwarded:[0 TO 150]"><code>amountAwarded:[0 TO 150]</code></a></li>
    <li class="red_underline">Amount Applied For between £800 and £1000: e.g. <a href="https://grantnav.threesixtygiving.org/search?text_query=amountAppliedFor:[800 TO 1000]"><code>amountAppliedFor:[800 TO 1000]</code></a></li>
  </ul>

  <p>You can also search ranges with one side unbounded:</p>

  <ul>
    <li class="red_underline"><a href="https://grantnav.threesixtygiving.org/search?text_query=amountAwarded:>1000"><code>amountAwarded:>1000</code></a> (more than 1000)</li>
    <li class="red_underline"><a href="https://grantnav.threesixtygiving.org/search?text_query=amountAwarded:>=1000"><code>amountAwarded:>=1000</code></a> (more than or equal to 1000)</li>
    <li class="red_underline"><a href="https://grantnav.threesixtygiving.org/search?text_query=amountAppliedFor:<1000"><code>amountAppliedFor:<1000</code></a> (less than 1000)</li>
    <li class="red_underline"><a href="https://grantnav.threesixtygiving.org/search?text_query=amountAppliedFor:<=1000"><code>amountAppliedFor:<=1000</code></a> (less than or equal to 1000)</li>
  </ul>

  <p class="red_underline">You can also use the * wildcard (see below) when asking for a range: e.g. <a href="https://grantnav.threesixtygiving.org/search?text_query=amountAwarded:[500 TO *]"><code>amountAwarded:[500 TO *]</code></a></p>
  <p>Searching for a range of values works alongside the Amount Awarded <a href="#filters">filter</a>. Therefore, you can search for a wide range of values and then refine, compare or see an overview of the distribution using the filter.

  <h3 id="wildcards">Wildcards</h3>
  <p class="red_underline">Wildcard searches can be run on individual terms, using ? to replace a single character, and * to replace zero or more characters: e.g.
    <a href="https://grantnav.threesixtygiving.org/search?text_query=b?g"><code>b?g</code></a>, <a href="https://grantnav.threesixtygiving.org/search?text_query=you*"><code>you*</code></a>. If you’re searching within a specific field, be aware that wildcard searching is only available on names, descriptive text fields, dates and amounts. 
  </p>

  <h3 id="fuzziness">Fuzziness</h3>
  <p class="red_underline">You can search for terms that are similar to, but not exactly like our search terms, using the “fuzzy” operator: ~ . To use it, put the ~ operator at the end of the term you’re looking for e.g.
    <a href="https://grantnav.threesixtygiving.org/search?text_query=youht~"><code>youht~</code></a>, <a href="https://grantnav.threesixtygiving.org/search?text_query=yung~"><code>yung~</code></a>, <a href="https://grantnav.threesixtygiving.org/search?text_query=pple~"><code>pple~</code></a>. Or, if you want to specify the ways in which the result can vary from the search term, then the wildcard operators are more appropriate. If you’re searching within a specific field, be aware that fuzzy matching is only available on names and descriptive text fields. 
  </p>

