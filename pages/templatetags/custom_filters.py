# custom_filters.py
from django import template

register = template.Library()

@register.filter
def number_to_letter(value):
    return chr(65 + value - 1)  # 65 is the ASCII value for 'A'