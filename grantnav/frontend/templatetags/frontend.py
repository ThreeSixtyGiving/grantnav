from django import template
import math

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

@register.filter(name='flatten')
def flatten(d):
    return {key: value for key, value in flatten_dict(d)}

@register.filter(name='half_sorted_items')
def half_grant(d, half):
    sorted_list = sorted(d.items(), key=lambda a: a[0].lower()) 
    if half == 1:
        return sorted_list[:math.floor(len(d)/2)]
    else:
        return sorted_list[math.floor(len(d)/2):]

   
