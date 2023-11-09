from django import template
register = template.Library()

@register.filter
def get_first_char(value):
    if value:
        return str(value)[0]
    else:
        return ""
