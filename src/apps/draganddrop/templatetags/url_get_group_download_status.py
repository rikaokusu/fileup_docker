from django import template
from datetime import datetime
import pytz
from accounts.models import User
from draganddrop.models import UrlUploadManage,Group,UrlDownloadtable
register = template.Library()

@register.filter
def url_get_group_download_status(group, upload_manage):

    # グループメンバー数の取得
    group_member_number = group.address.all().count()

    # ダウンロード済みのグループメンバーの数を取得
    user_list = []
    for user in group.address.all():
        user_list.append(user.id)
    downloaded_user_number = UrlDownloadtable.objects.filter(url_upload_manage=upload_manage, dest_user__in=user_list, is_downloaded=True).count()

    if group_member_number == downloaded_user_number:
        return True

    else:
        return False