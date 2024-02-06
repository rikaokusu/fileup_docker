from django import template
from datetime import datetime
import pytz
from accounts.models import User
from draganddrop.models import UploadManage, Downloadtable, Address
register = template.Library()


@register.filter
def get_direct_users(upload_manage):
    """ dest_user_allに直接入力のアドレスとアドレス帳から選択したユーザーをqsでセットする """
        
    direct_user = []

    #送信先ユーザーのクエリーセット
    upload_manage_dest_user_all = upload_manage.dest_user.all()

    direct_user_qs = Address.objects.filter(email__in=direct_user)

    print('アドレス帳？？',upload_manage_dest_user_all)
    print('アドレス帳？？22',direct_user_qs)

    dest_user_all = upload_manage_dest_user_all | direct_user_qs
    print('アドレス帳？？合計',dest_user_all)

    return dest_user_all
    