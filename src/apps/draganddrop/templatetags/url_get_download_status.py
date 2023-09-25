from django import template
from datetime import datetime
import pytz
from accounts.models import User
from draganddrop.models import UrlUploadManage, UrlDownloadtable
register = template.Library()


@register.filter
def url_get_download_status(model_obj, value):
    urldownloadtable = UrlDownloadtable.objects.filter(dest_user=value, url_upload_manage=model_obj).first()

    if urldownloadtable:
        return urldownloadtable.is_downloaded

    else:
        return None
