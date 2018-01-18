CURRENCY_SYMBOLS = {
    'GBP': '£',
    'USD': '$'
}


def currency_prefix(currency):
    if not currency:
        return ''
    if currency.upper() == 'GBP':
        return '£'
    if currency:
        return currency + ' '
