from django import template
import os.path

register = template.Library()

@register.filter
def get_extention(value):
    return os.path.splitext(value)[1]

