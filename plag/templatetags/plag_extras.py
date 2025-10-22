from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    """Split string by delimiter"""
    if value:
        return value.split(delimiter)
    return []