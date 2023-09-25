from django import template
from datetime import date, datetime, timezone, timedelta
import calendar
import pytz
from django.utils.timezone import make_aware
register = template.Library()

@register.filter
def url_dl_count(qs, file_id):
    url_download_file = qs.filter(download_file=file_id).first()

    return url_download_file.url_dl_count
