from django import template

register = template.Library()

@register.filter(name='get_value_by_key')
def get_value_by_key(data, key):
    return data.get(key, "")