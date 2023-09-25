from django import template
import datetime

register = template.Library()

@register.filter
def check_date(date):
    tody = datetime.date.today()
    # 試用期間終了前の場合はTrueを返す
    return tody < date
