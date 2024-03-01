from django import template
from datetime import datetime
import pytz
from accounts.models import User
from draganddrop.models import UploadManage, Downloadtable, Address
register = template.Library()


@register.filter
def get_display_company(user):
    """ 送信テーブルの送信者用データ"""
    # dest_userをsessionに追加するためQSをリスト化して保存。
    # if user.company_name and not user.legal_personality == 99:
    #     if user.legal_person_posi == 1:
    #         dest_user_display_name = user.get_legal_personality_display() + user.company_name + " " + user.last_name + "" + user.first_name
    #     else:
    #         dest_user_display_name = user.company_name + user.get_legal_personality_display() + " " + user.last_name + "" + user.first_name
    # elif user.company_name and user.legal_personality == 99:
    #     dest_user_display_name = user.company_name +" " + user.last_name + "" + user.first_name
    # elif user.trade_name:
    #     dest_user_display_name = user.trade_name + " " + user.last_name + "" + user.first_name
    # else:
    #     dest_user_display_name = user.email
    
    if user.company_name and not user.legal_personality == 99:
        if user.legal_person_posi == 1:
            if user.department_name:
                dest_user_display_name = user.get_legal_personality_display() + user.company_name + '　' + user.department_name
            else:
                dest_user_display_name = user.get_legal_personality_display() + user.company_name
        else:
            if user.department_name:
                dest_user_display_name = user.company_name + user.get_legal_personality_display() + '　' + user.department_name
            else:
                dest_user_display_name = user.company_name + user.get_legal_personality_display()
    elif user.company_name and user.legal_personality == 99:
        if user.department_name:
            dest_user_display_name = user.company_name + '　' + user.department_name
        else:
            dest_user_display_name = user.company_name
    elif user.trade_name:
        dest_user_display_name = user.trade_name
    else:
        dest_user_display_name = user.email

    return dest_user_display_name
