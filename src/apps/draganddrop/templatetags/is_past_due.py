from django import template
from datetime import date, datetime, timezone, timedelta
import calendar
import pytz
from django.utils.timezone import make_aware
register = template.Library()

@register.filter
def is_past_due(value):

    date = make_aware(datetime.now())

    return date > value
