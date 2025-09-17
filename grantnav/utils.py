import subprocess
from django.shortcuts import redirect
from urllib.parse import urlencode, urlparse, parse_qs


CURRENCY_SYMBOLS = {
    'GBP': '£',
    'USD': '$',
    'EUR': '€',
}


def currency_prefix(currency):
    if not currency:
        return ''
    if currency.upper() == 'GBP':
        return '£'
    if currency:
        return currency + ' '


def yearmonth_to_date(yearmonth, max=False):
    ''' Convert YYYY/MM into YYYY-MM-DD, yeardate is from url so has to be checked'''
    date_split = yearmonth.split('/')
    if len(date_split) != 2:
        return
    month, year = date_split
    try:
        month, year = int(month), int(year)
        # need first day of next month
        if max:
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1
    except ValueError:
        return
    return f'{year}-{month:02}-01'


def date_to_yearmonth(date, max=False):
    ''' Convert YYYY-MM-DD into YYYY/MM, date is from internal representations so safe'''
    if not date:
        return ''
    date_split = [int(part) for part in date.split('-')]
    year, month, day = date_split

    if max:
        # need first day of previous month
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1

    return f'{month:02}/{year}'


def get_git_revision():
    try:
        return subprocess.check_output(
            ["git show --format=format:%h  --no-patch"], shell=True
        ).decode()

    except subprocess.CalledProcessError:
        return 'Unknown'


def internal_redirect(to):
    """ Adds a flag to allow the webserver to know that an "internal"
        redirect has taken place.

        Returns: HttpResponseRedirect
    """

    parsed_url = urlparse(to)
    query_params = parse_qs(parsed_url.query)
    query_params["_redirect_src"] = ["int"]

    # Reconstruct the query string
    new_query_string = urlencode(query_params, doseq=True)

    # Reconstruct the URL
    new_url = parsed_url._replace(query=new_query_string).geturl()

    return redirect(new_url)


def check_if_tnlcommunityfund_legacy_json_query(json_query_str):
    """ Determine if this is legacy mode link from tnlcommunityfund website
        and redirect accordingly. This can be removed when the link from
        https://www.tnlcommunityfund.org.uk/funding is updated.
    """
    # Test url:
    # https://grantnav.threesixtygiving.org/search?json_query=%7B%22query%22%3A+%7B%22bool%22%3A+%7B%22filter%22%3A+%5B%7B%22bool%22%3A+%7B%22should%22%3A+%5B%7B%22term%22%3A+%7B%22fundingOrganization.id_and_name%22%3A+%22%5B%5C%22The+National+Lottery+Community+Fund%5C%22%2C+%5C%22GB-GOR-PB188%5C%22%5D%22%7D%7D%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%2C+%22must%22%3A+%7B%7D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%7B%22range%22%3A+%7B%22amountAwarded%22%3A+%7B%7D%7D%7D%2C+%22must%22%3A+%7B%7D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%2C+%7B%22bool%22%3A+%7B%22should%22%3A+%5B%5D%7D%7D%5D%2C+%22must%22%3A+%7B%22query_string%22%3A+%7B%22default_field%22%3A+%22%2A%22%2C+%22query%22%3A+%22%2A%22%7D%7D%7D%7D%2C+%22sort%22%3A+%7B%22_score%22%3A+%7B%22order%22%3A+%22desc%22%7D%7D%2C+%22aggs%22%3A+%7B%22recipientDistrictName%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22recipientDistrictName%22%7D%7D%2C+%22currency%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22currency%22%7D%7D%2C+%22recipientOrganization%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22recipientOrganization.id_and_name%22%7D%7D%2C+%22fundingOrganization%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22fundingOrganization.id_and_name%22%7D%7D%2C+%22recipientRegionName%22%3A+%7B%22terms%22%3A+%7B%22size%22%3A+3%2C+%22field%22%3A+%22recipientRegionName%22%7D%7D%7D%2C+%22extra_context%22%3A+%7B%22awardYear_facet_size%22%3A+3%2C+%22amountAwardedFixed_facet_size%22%3A+3%7D%7D
    #

    tnl_query = '{"query": {"bool": {"filter": [{"bool": {"should": [{"term": {"fundingOrganization.id_and_name": "[\\"The National Lottery Community Fund\\", \\"GB-GOR-PB188\\"]"}}]}}, {"bool": {"should": []}}, {"bool": {"should": [], "must": {}}}, {"bool": {"should": {"range": {"amountAwarded": {}}}, "must": {}}}, {"bool": {"should": []}}, {"bool": {"should": []}}, {"bool": {"should": []}}, {"bool": {"should": []}}], "must": {"query_string": {"default_field": "*", "query": "*"}}}}, "sort": {"_score": {"order": "desc"}}, "aggs": {"recipientDistrictName": {"terms": {"size": 3, "field": "recipientDistrictName"}}, "currency": {"terms": {"size": 3, "field": "currency"}}, "recipientOrganization": {"terms": {"size": 3, "field": "recipientOrganization.id_and_name"}}, "fundingOrganization": {"terms": {"size": 3, "field": "fundingOrganization.id_and_name"}}, "recipientRegionName": {"terms": {"size": 3, "field": "recipientRegionName"}}}, "extra_context": {"awardYear_facet_size": 3, "amountAwardedFixed_facet_size": 3}}'

    if tnl_query == json_query_str:
        return internal_redirect("/search?fundingOrganization=GB-GOR-PB188&fundingOrganization=GB-GOVUK-big-lottery-fund&a=1")

    return False
