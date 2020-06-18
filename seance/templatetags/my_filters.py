from django import template


register = template.Library()


@register.filter(name='range')
def filter_range(start, end):
    return list(range(start, end+1))


@register.simple_tag()
def get_item(dictionary, key):
    return dictionary.get(key)

