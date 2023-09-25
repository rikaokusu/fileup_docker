from django import template
from datetime import date, datetime, timezone, timedelta
import calendar
import pytz
from django.utils.timezone import make_aware
register = template.Library()

@register.filter
def dl_count(qs, file_id):
    download_file = qs.filter(download_file=file_id).first()

    return download_file.dl_count
