from django import template

register = template.Library()

@register.filter(name='is_list')
def is_list(data):
    return isinstance(data, list)