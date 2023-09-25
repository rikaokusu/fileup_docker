from django import template
from datetime import datetime
import pytz
from accounts.models import User
from draganddrop.models import UploadManage, Downloadtable, Address
register = template.Library()


@register.filter
def get_display_name(user):
    """ 送信テーブルの送信者用データ"""
    # dest_userをsessionに追加するためQSをリスト化して保存。

    if user.company_name:
        dest_user_display_name = user.company_name +" " + user.last_name + "" + user.first_name
    elif (user.company_name == None) and (user.last_name):
        dest_user_display_name =  user.last_name + "" + user.first_name
    elif user.trade_name:
        dest_user_display_name = user.trade_name +" " + user.last_name + "" + user.first_name
    else:
        dest_user_display_name = user.email
        
    return dest_user_display_name
