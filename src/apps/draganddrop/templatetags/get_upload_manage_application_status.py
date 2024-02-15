from django import template
from datetime import datetime
import pytz
from accounts.models import User
from draganddrop.models import UploadManage, UrlUploadManage, ApprovalManage, ApprovalLog
register = template.Library()


@register.filter
def get_upload_manage_application_status(value):
    """ アップロード方法ごとにupload_manageのapplication_statusを取得して返す"""
    print("--------------- get_upload_manage_application_status", value)

    if value.upload_method == 1:
        print("------------------------- 通常アップロード")
        return value.upload_manage.application_status

    elif value.upload_method == 2:
        print("------------------------- URL共有")
        return value.url_upload_manage.application_status

    elif value.upload_method == 3:
        print("------------------------- OPT共有")
        return value.otp_upload_manage.application_status

    else:
        print("------------------------- ゲストアップロード")
        return value.guest_upload_manage.application_status