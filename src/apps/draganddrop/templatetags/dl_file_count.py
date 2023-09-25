from django import template
from datetime import date, datetime, timezone, timedelta
import calendar
import pytz
from django.utils.timezone import make_aware
register = template.Library()

@register.filter
def dl_file_count(qs, dl_limit):
    
    dl_status = []

    for download_file in qs:
        
        dl_file_status = download_file.dl_count < dl_limit #DL制限を超えていない場合はTrue
        dl_status.append(dl_file_status)

    dl_ok = dl_status.count(True)

    return dl_ok

    




    








    # 配列 = ファイルごとのdl_count < dl_limit
    # 配列の中はリスト化されているので[True, False, True]といった感じでデータが格納される。
    # dl_ok = 配列.count("False")
    # ここまでがテンプレートタグ

    # その後テンプレートに戻ってifの条件式でボタンの有効無効を分岐させる。
    # zipファイルの中に一つでもfalseがある場合は無効にする。

    # elif dl_ok|dl_file_count: dest_user_data.upload_manage.dl_limit >= 1 
    