# your_app/templatetags/custom_tags.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def make_range(current, total):
    start = max(1, current - 2)
    end = min(total, current + 2)
    return range(start, end + 1)