from django import template
from datetime import datetime
import pytz
from accounts.models import User
from draganddrop.models import UploadManage, UrlUploadManage, ApprovalManage, ApprovalLog
register = template.Library()


@register.filter
def get_upload_manage_title(value):
    """ アップロード方法ごとにupload_manageのtitleを取得して返す"""

    # 通常アップロード
    if value.upload_method == 1:
        # print("------------------------- 通常アップロード")
        return value.upload_manage.title
    # URL共有
    elif value.upload_method == 2:
        # print("------------------------- URL共有")
        return value.url_upload_manage.title
    # OPT共有
    elif value.upload_method == 3:
        # print("------------------------- OPT共有")
        return value.opt_upload_manage.title
    # ゲストアップロード
    else:
        # print("------------------------- ゲストアップロード")
        return value.guest_upload_manage.title
