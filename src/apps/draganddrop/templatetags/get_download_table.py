from django import template
from datetime import datetime
import pytz
from accounts.models import User
from draganddrop.models import UploadManage, Downloadtable
register = template.Library()


@register.filter
def get_download_table(value):
    """ Downloadtableを取得"""
    # print("--------------- Downloadtableを取得")
    # print("--------------- value", value)# アップロード1
    # print("--------------- user_approval_manage id", value.id)# 4f69524d-5d60-44c0-8bff-f5f360896487

    upload_manage = UploadManage.objects.filter(id=value).first()
    # print("--------------- upload_manage", upload_manage)

    download_table = Downloadtable.objects.filter(upload_manage=upload_manage).first()
    # print("--------------- download_table", download_table)

    return download_table.id
