from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """
    Split a string by delimiter and return a list of items.
    Usage: {{ "1=Poor,2=Fair,3=Good"|split:"," }}
    """
    return [item.strip() for item in value.split(arg)] 