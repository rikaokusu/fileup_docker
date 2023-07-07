from django import template
from datetime import datetime, date, timedelta, timezone
from dateutil.relativedelta import relativedelta
import pytz
register = template.Library()

@register.filter
def is_onemonthago(date):
    today = datetime.now(timezone.utc)
    one_month_ago = date - relativedelta(months=1)
    # 一ヶ月前はTrueを返す
    return one_month_ago < today
