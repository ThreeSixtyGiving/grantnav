from django import template
import math
import datetime
import dateutil.parser as date_parser
import strict_rfc3339
import json

register = template.Library()


@register.filter(name='get')
def get(d, k):
    return d.get(k, None)


def flatten_dict(data, path=tuple()):
    for key, value in data.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    yield from flatten_dict(item, path + (key,))
        elif isinstance(value, dict):
            yield from flatten_dict(value, path + (key,))
        else:
            yield ": ".join(path + (key,)), value

SKIP_KEYS = ["id", "title", "description",
             "amountAwarded", "currency",
             "awardDate", "recipientOrganization: name",
             "recipientOrganization: id",
             "fundingOrganization: name",
             "fundingOrganization: id"]


@register.filter(name='flatten')
def flatten(d):
    return {key: value for key, value in flatten_dict(d)
            if key not in SKIP_KEYS}


@register.filter(name='half_sorted_items')
def half_grant(grant, half):
    sorted_list = sorted(grant.items(), key=lambda a: a[0].lower())
    if half == 1:
        return sorted_list[:math.floor(len(grant) / 2)]
    else:
        return sorted_list[math.floor(len(grant) / 2):]


@register.filter(name='get_title')
def get_title(d):
    title = d.get('title')
    if title:
        return title
    else:
        return d.get('id')


@register.filter(name='get_name')
def get_name(d):
    name = d.get('name')
    if name:
        return name
    else:
        return d.get('id')


@register.filter(name='get_currency')
def get_currency(d):
    currency = d.get('currency')
    if not currency:
        return ''
    if currency.lower() == 'gbp':
        return '£'
    else:
        return currency + ' '


@register.filter(name='get_amount')
def get_amount(amount):
    try:
        return "{:,.0f}".format(amount)
    except ValueError:
        return amount


@register.filter(name='get_date')
def get_date(date):
    valid = strict_rfc3339.validate_rfc3339(date)
    if not valid:
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return date
    
    return date_parser.parse(date, dayfirst=True).strftime("%d %b %Y")


@register.filter(name='get_amount_range')
def get_amount_range(bucket):
    from_ = get_amount(int(bucket.get('from')))
    to_ = bucket.get('to')
    if to_:
        to_ = get_amount(int(to_))
    if to_ == from_:
        return from_
    if not to_:
        return '£' + from_ + ' +'
    return '£' + from_ + ' - ' + '£' + to_


@register.filter(name='get_facet_org_name')
def get_facet_org_name(facet):
    return json.loads(facet)[1]
