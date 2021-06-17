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
