from django import template

register = template.Library()


@register.filter(name="csvify")
def csvify(value):
    return value.replace("\n", ",")


@register.filter(name='get')
def get(d, k):
    return d.get(k, None)
