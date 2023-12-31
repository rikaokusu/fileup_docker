from django import template
from datetime import datetime
import pytz
from accounts.models import User
from draganddrop.models import OTPUploadManage, OTPDownloadtable, Address
register = template.Library()


@register.filter
def otp_get_direct_users(otp_upload_manage):
    """ dest_user_allに直接入力のアドレスとアドレス帳から選択したユーザーをqsでセットする """

    direct_user = []
    
    #送信先ユーザーのクエリーセット
    otp_upload_manage_dest_user_all = otp_upload_manage.dest_user.all()

    direct_user_qs = Address.objects.filter(email__in=direct_user)

    dest_user_all = otp_upload_manage_dest_user_all | direct_user_qs

    return dest_user_all
