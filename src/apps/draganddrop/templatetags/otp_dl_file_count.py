from django import template
from datetime import date, datetime, timezone, timedelta
import calendar
import pytz
from django.utils.timezone import make_aware
register = template.Library()

@register.filter
def otp_dl_file_count(qs, otp_dl_limit):
    
    otp_dl_status = []

    for otp_download_file in qs:
        
        otp_dl_file_status = otp_download_file.otp_dl_count < otp_dl_limit #DL制限を超えていない場合はTrue
        otp_dl_status.append(otp_dl_file_status)
    otp_dl_ok = otp_dl_status.count(True)
    return otp_dl_ok



    # 配列 = ファイルごとのdl_count < dl_limit
    # 配列の中はリスト化されているので[True, False, True]といった感じでデータが格納される。
    # dl_ok = 配列.count("False")
    # ここまでがテンプレートタグ

    # その後テンプレートに戻ってifの条件式でボタンの有効無効を分岐させる。
    # zipファイルの中に一つでもfalseがある場合は無効にする。

    # elif dl_ok|dl_file_count: dest_user_data.upload_manage.dl_limit >= 1 
    